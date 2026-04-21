import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from urllib import error, request

from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.workspace import Workspace


from app.api.deps import get_current_user
from app.core.config import settings
from app.core.db import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership

try:
    import stripe  # type: ignore
except ImportError:
    stripe = None


router = APIRouter(prefix="/billing", tags=["billing"])

from fastapi import HTTPException

@router.get("/workspace/{workspace_id}")
def get_workspace_billing(workspace_id: int, db: Session = Depends(get_db)):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return {
        "workspace_id": workspace.id,
        "plan": getattr(workspace, "plan_code", "starter"),
        "billing_status": getattr(workspace, "billing_status", "inactive"),
        "claims_used": getattr(workspace, "claims_used", 0),
    }


class BillingCheckoutPayload(BaseModel):
    plan_code: str | None = Field(default=None, min_length=1, max_length=50)
    target_plan_code: str | None = Field(default=None, min_length=1, max_length=50)
    billing_cycle: str = Field(default="monthly", min_length=1, max_length=20)

    @model_validator(mode="after")
    def ensure_plan_code_present(self):
        resolved = self.plan_code or self.target_plan_code
        if not resolved:
            raise ValueError("Either plan_code or target_plan_code is required")
        self.plan_code = resolved
        return self


class BillingPortalPayload(BaseModel):
    return_url: str | None = None


def require_workspace_member(workspace_id: int, current_user: User, db: Session):
    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        .first()
    )
    if not membership:
        return None
    return membership


def require_workspace_owner(workspace_id: int, current_user: User, db: Session):
    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(status_code=403, detail="Not a workspace member")

    if membership.role != "owner":
        raise HTTPException(status_code=403, detail="Owner role required")

    return membership


def normalize_plan_code(plan_code: str | None) -> str:
    allowed = {"sandbox", "starter", "pro", "growth", "business"}
    value = str(plan_code or "").strip().lower()
    return value if value in allowed else "starter"


def normalize_billing_cycle(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    if normalized == "yearly":
        normalized = "annual"
    return normalized if normalized in {"monthly", "annual"} else "monthly"


def normalize_billing_status(value: str | None) -> str:
    allowed = {
        "inactive",
        "active",
        "trialing",
        "past_due",
        "canceled",
        "unpaid",
        "pending_manual_review",
    }
    normalized = str(value or "").strip().lower()
    return normalized if normalized in allowed else "inactive"


def is_paid_billing_status(value: str | None) -> bool:
    return normalize_billing_status(value) in {"active", "trialing"}


def resolve_effective_plan_code(workspace: Workspace) -> str:
    configured_plan = normalize_plan_code(workspace.plan_code)
    billing_status = normalize_billing_status(workspace.billing_status)

    if configured_plan in {"sandbox", "starter"}:
        return configured_plan

    if is_paid_billing_status(billing_status):
        return configured_plan

    return "starter"


def map_stripe_subscription_status(value: str | None) -> str:
    normalized = str(value or "").strip().lower()

    if normalized in {"trialing", "active", "past_due", "canceled", "unpaid"}:
        return normalized

    if normalized in {"incomplete", "incomplete_expired", "paused"}:
        return "inactive"

    return "inactive"


def map_paddle_subscription_status(value: str | None) -> str:
    normalized = str(value or "").strip().lower()

    if normalized in {"active", "trialing", "past_due", "canceled"}:
        return normalized

    if normalized in {"paused", "inactive"}:
        return "inactive"

    return "inactive"


def unix_to_datetime(value) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).replace(tzinfo=None)
    except Exception:
        return None


def parse_iso_datetime(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None

    candidates = [
        text,
        text.replace("Z", "+00:00"),
    ]
    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is not None:
                return parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return parsed
        except Exception:
            continue

    return None


def fallback_period_end_for_cycle(billing_cycle: str) -> datetime:
    now = datetime.utcnow()
    if normalize_billing_cycle(billing_cycle) == "annual":
        return now + timedelta(days=365)
    return now + timedelta(days=30)


def get_plan_catalog():
    return [
        {
            "code": "sandbox",
            "name": "Sandbox",
            "limits": {
                "member_limit": 3,
                "trade_limit": 1000,
                "claim_limit": 5,
                "storage_limit_mb": 100,
            },
            "billing": {
                "monthly_price_usd": 0,
                "annual_price_usd": 0,
                "stripe_price_lookup_key_monthly": None,
                "stripe_price_lookup_key_annual": None,
            },
        },
        {
            "code": "starter",
            "name": "Starter",
            "limits": {
                "member_limit": 3,
                "trade_limit": 5000,
                "claim_limit": 5,
                "storage_limit_mb": 500,
            },
            "billing": {
                "monthly_price_usd": 19,
                "annual_price_usd": 190,
                "stripe_price_lookup_key_monthly": "ttl_starter_monthly",
                "stripe_price_lookup_key_annual": "ttl_starter_annual",
            },
        },
        {
            "code": "pro",
            "name": "Pro",
            "limits": {
                "member_limit": 25,
                "trade_limit": 50000,
                "claim_limit": 50,
                "storage_limit_mb": 2048,
            },
            "billing": {
                "monthly_price_usd": 79,
                "annual_price_usd": 790,
                "stripe_price_lookup_key_monthly": "ttl_pro_monthly",
                "stripe_price_lookup_key_annual": "ttl_pro_annual",
            },
        },
        {
            "code": "growth",
            "name": "Growth",
            "limits": {
                "member_limit": 100,
                "trade_limit": 250000,
                "claim_limit": 200,
                "storage_limit_mb": 10240,
            },
            "billing": {
                "monthly_price_usd": 249,
                "annual_price_usd": 2490,
                "stripe_price_lookup_key_monthly": "ttl_growth_monthly",
                "stripe_price_lookup_key_annual": "ttl_growth_annual",
            },
        },
        {
            "code": "business",
            "name": "Business",
            "limits": {
                "member_limit": 250,
                "trade_limit": 1000000,
                "claim_limit": 500,
                "storage_limit_mb": 51200,
            },
            "billing": {
                "monthly_price_usd": 999,
                "annual_price_usd": 9990,
                "stripe_price_lookup_key_monthly": "ttl_business_monthly",
                "stripe_price_lookup_key_annual": "ttl_business_annual",
            },
        },
    ]


def get_plan_definition(plan_code: str | None):
    normalized = normalize_plan_code(plan_code)
    for plan in get_plan_catalog():
        if plan["code"] == normalized:
            return plan
    return get_plan_catalog()[0]


def get_workspace_plan_snapshot(plan_code: str | None) -> dict:
    plan = get_plan_definition(plan_code)
    limits = plan.get("limits", {}) or {}
    return {
        "plan_code": plan["code"],
        "plan_name": plan["name"],
        "member_limit": int(limits.get("member_limit") or 0),
        "trade_limit": int(limits.get("trade_limit") or 0),
        "claim_limit": int(limits.get("claim_limit") or 0),
        "storage_limit_mb": int(limits.get("storage_limit_mb") or 0),
    }


def apply_workspace_plan_limits(workspace: Workspace, plan_code: str | None) -> None:
    snapshot = get_workspace_plan_snapshot(plan_code)
    workspace.member_limit = snapshot["member_limit"]
    workspace.trade_limit = snapshot["trade_limit"]
    workspace.claim_limit = snapshot["claim_limit"]
    workspace.storage_limit_mb = snapshot["storage_limit_mb"]


def get_frontend_base_url() -> str:
    value = settings.FRONTEND_BASE_URL or "http://localhost:3000"
    return value.rstrip("/")


def get_active_billing_provider(workspace: Workspace) -> str:
    provider = str(workspace.billing_provider or "").strip().lower()
    if provider in {"paddle", "stripe", "manual"}:
        return provider

    if paddle_is_ready():
        return "paddle"
    if stripe_is_ready():
        return "stripe"
    if manual_billing_is_ready():
        return "manual"
    return "none"


def get_billing_provider_display_label(provider: str | None) -> str:
    normalized = str(provider or "").strip().lower()
    if normalized == "paddle":
        return "Paddle"
    if normalized == "stripe":
        return "Stripe"
    if normalized == "manual":
        return "Manual Billing"
    return "Unconfigured"


def get_paddle_environment() -> str:
    base_url = paddle_api_base_url().lower()
    api_key = str(getattr(settings, "PADDLE_API_KEY", "") or "").strip().lower()

    if "sandbox" in base_url or api_key.startswith("test_") or api_key.startswith("pdl_sdbx"):
        return "sandbox"
    return "live"


def should_expose_manual_billing(workspace: Workspace) -> bool:
    if not manual_billing_is_ready():
        return False

    active_provider = get_active_billing_provider(workspace)

    # Hide manual instructions when Paddle or Stripe automation is already active.
    if active_provider in {"paddle", "stripe"}:
        return False

    return True


def get_provider_customer_id(workspace: Workspace, provider: str | None) -> str | None:
    normalized = str(provider or "").strip().lower()
    if normalized == "paddle":
        return workspace.paddle_customer_id
    if normalized == "stripe":
        return workspace.stripe_customer_id
    return None


def get_provider_subscription_id(workspace: Workspace, provider: str | None) -> str | None:
    normalized = str(provider or "").strip().lower()
    if normalized == "paddle":
        return workspace.paddle_subscription_id
    if normalized == "stripe":
        return workspace.stripe_subscription_id
    return None


def get_checkout_return_url(workspace_id: int) -> str:
    return f"{get_frontend_base_url()}/workspace/{workspace_id}/settings"


def get_price_lookup_key(plan_code: str, billing_cycle: str) -> str:
    plan = get_plan_definition(plan_code)
    billing = plan.get("billing", {})

    if billing_cycle == "annual":
        return str(billing.get("stripe_price_lookup_key_annual") or "").strip()
    return str(billing.get("stripe_price_lookup_key_monthly") or "").strip()


def get_paddle_price_catalog() -> dict[str, str]:
    return {
        "sandbox_monthly": "",
        "sandbox_annual": "",
        "starter_monthly": "pri_01kmfd0qzs6qv96wqgtjj73xn7",
        "starter_annual": "pri_01kmfddg7sej6n5rftg2nv55sm",
        "pro_monthly": "pri_01kmfdh1nf9cpf4mvzt6r9eh2h",
        "pro_annual": "pri_01kmfdqzqfpf6081acqmht1znw",
        "growth_monthly": "pri_01kmfdyggmwmqngg5y0t6qrzsc",
        "growth_annual": "pri_01kmfe1tjzf9pd7fswkcfycf2h",
        "business_monthly": "pri_01kmfe56ft09081tf3127vkz8w",
        "business_annual": "pri_01kmfe9k5hsdxcm6bj90ycjy0q",
    }


def get_paddle_price_id(plan_code: str, billing_cycle: str) -> str | None:
    key = f"{normalize_plan_code(plan_code)}_{normalize_billing_cycle(billing_cycle)}"
    return get_paddle_price_catalog().get(key)


def get_workspace_for_owner_access(
    workspace_id: int,
    db: Session,
    current_user: User,
) -> tuple[Workspace | None, str | None]:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        return None, "Workspace not found"

    membership = require_workspace_owner(workspace_id, current_user, db)
    if not membership:
        return None, "Owner role required for this workspace"

    return workspace, None


def stripe_is_ready() -> bool:
    return bool(
        getattr(settings, "STRIPE_BILLING_ENABLED", False)
        and stripe is not None
        and settings.STRIPE_SECRET_KEY
        and settings.STRIPE_SECRET_KEY.strip()
    )


def paddle_is_ready() -> bool:
    return bool(
        getattr(settings, "PADDLE_BILLING_ENABLED", True)
        and getattr(settings, "PADDLE_API_KEY", None)
        and str(settings.PADDLE_API_KEY).strip()
        and get_paddle_price_catalog()
    )


def manual_billing_is_ready() -> bool:
    return bool(
        getattr(settings, "MANUAL_BILLING_ENABLED", False)
        and (
            (
                getattr(settings, "MANUAL_PAYMENT_ACCOUNT_NUMBER", None)
                and str(settings.MANUAL_PAYMENT_ACCOUNT_NUMBER).strip()
            )
            or (
                getattr(settings, "MANUAL_PAYMENT_PHONE_NUMBER", None)
                and str(settings.MANUAL_PAYMENT_PHONE_NUMBER).strip()
            )
        )
    )


def get_manual_payment_details() -> dict:
    return {
        "enabled": bool(getattr(settings, "MANUAL_BILLING_ENABLED", False)),
        "payment_method": getattr(settings, "MANUAL_PAYMENT_METHOD", None),
        "account_name": getattr(settings, "MANUAL_PAYMENT_ACCOUNT_NAME", None),
        "account_number": getattr(settings, "MANUAL_PAYMENT_ACCOUNT_NUMBER", None),
        "bank_name": getattr(settings, "MANUAL_PAYMENT_BANK_NAME", None),
        "phone_number": getattr(settings, "MANUAL_PAYMENT_PHONE_NUMBER", None),
        "notes": getattr(settings, "MANUAL_PAYMENT_NOTES", None),
    }


def configure_stripe() -> tuple[bool, str | None]:
    if stripe is None:
        return False, "Stripe package is not installed."
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_SECRET_KEY.strip():
        return False, "STRIPE_SECRET_KEY is not configured."
    stripe.api_key = settings.STRIPE_SECRET_KEY.strip()
    return True, None

    
def paddle_api_base_url() -> str:
    return str(getattr(settings, "PADDLE_API_BASE_URL", "https://api.paddle.com")).rstrip("/")


def paddle_request(method: str, path: str, payload: dict | None = None) -> tuple[dict | None, str | None]:
    api_key = str(getattr(settings, "PADDLE_API_KEY", "") or "").strip()
    if not api_key:
        return None, "PADDLE_API_KEY is not configured."

    url = f"{paddle_api_base_url()}{path}"
    body = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(
        url=url,
        data=body,
        method=method.upper(),
        headers=headers,
    )

    try:
        with request.urlopen(req, timeout=45) as response:
            raw = response.read().decode("utf-8")
            if not raw:
                return {}, None
            return json.loads(raw), None
    except error.HTTPError as exc:
        try:
            raw = exc.read().decode("utf-8")
            parsed = json.loads(raw) if raw else {}
        except Exception:
            parsed = {}

        detail = (
            parsed.get("error", {}).get("detail")
            or parsed.get("detail")
            or parsed.get("errors")
            or str(exc)
        )
        return None, f"Paddle API request failed: {detail}"
    except Exception as exc:
        return None, f"Paddle API request failed: {exc}"


def get_or_create_stripe_customer(
    workspace: Workspace,
    current_user: User,
    db: Session,
):
    ok, error_message = configure_stripe()
    if not ok:
        return None, error_message

    if workspace.stripe_customer_id and workspace.stripe_customer_id.strip():
        try:
            customer = stripe.Customer.retrieve(workspace.stripe_customer_id.strip())
            deleted = getattr(customer, "deleted", False)
            if not deleted:
                return customer, None
        except Exception:
            pass

    email = (workspace.billing_email or current_user.email or "").strip()
    if not email:
        return None, "A billing email or user email is required before creating a Stripe customer."

    try:
        customer = stripe.Customer.create(
            email=email,
            name=workspace.name,
            metadata={
                "workspace_id": str(workspace.id),
                "workspace_name": workspace.name,
                "owner_user_id": str(current_user.id),
            },
        )
    except Exception as exc:
        return None, f"Stripe customer creation failed: {exc}"

    workspace.billing_provider = "stripe"
    workspace.stripe_customer_id = getattr(customer, "id", None)
    workspace.billing_email = email
    workspace.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(workspace)

    return customer, None


def resolve_stripe_price_id_from_lookup_key(lookup_key: str) -> tuple[str | None, str | None]:
    ok, error_message = configure_stripe()
    if not ok:
        return None, error_message

    if not lookup_key:
        return None, "Could not resolve Stripe lookup key for selected plan."

    try:
        result = stripe.Price.list(
            lookup_keys=[lookup_key],
            active=True,
            limit=1,
            expand=["data.product"],
        )
    except Exception as exc:
        return None, f"Stripe price lookup failed: {exc}"

    data = getattr(result, "data", None) or []
    if not data:
        return None, (
            f"No active Stripe Price found for lookup key '{lookup_key}'. "
            "Create the Price in Stripe and set its lookup key correctly."
        )

    price = data[0]
    price_id = getattr(price, "id", None)
    if not price_id:
        return None, f"Stripe returned a price for lookup key '{lookup_key}', but it has no id."

    return price_id, None


def can_start_checkout_for_target_plan(workspace: Workspace, target_plan_code: str) -> bool:
    configured_plan_code = normalize_plan_code(workspace.plan_code)
    target_normalized = normalize_plan_code(target_plan_code)
    billing_status = normalize_billing_status(workspace.billing_status)

    if target_normalized == "sandbox":
        return target_normalized != configured_plan_code

    if target_normalized != configured_plan_code:
        return True

    if configured_plan_code in {"sandbox", "starter"}:
        return False

    return not is_paid_billing_status(billing_status)


def checkout_intent_for_target_plan(workspace: Workspace, target_plan_code: str) -> str:
    configured_plan_code = normalize_plan_code(workspace.plan_code)
    target_normalized = normalize_plan_code(target_plan_code)

    if target_normalized == "sandbox":
        return "sandbox_activation" if target_normalized != configured_plan_code else "no_op"

    if target_normalized != configured_plan_code:
        return "plan_change"

    if target_normalized in {"sandbox", "starter"}:
        return "no_op"

    if is_paid_billing_status(workspace.billing_status):
        return "no_op"

    return "billing_activation"


def update_workspace_billing_from_subscription(
    workspace: Workspace,
    subscription,
    db: Session,
):
    metadata = getattr(subscription, "metadata", {}) or {}

    target_plan_code = metadata.get("target_plan_code")
    status = getattr(subscription, "status", None)
    current_period_end = getattr(subscription, "current_period_end", None)

    workspace.billing_provider = "stripe"
    workspace.stripe_subscription_id = getattr(subscription, "id", None)
    workspace.subscription_current_period_end = unix_to_datetime(current_period_end)
    workspace.billing_status = map_stripe_subscription_status(status)

    if target_plan_code:
        workspace.plan_code = normalize_plan_code(target_plan_code)

    apply_workspace_plan_limits(workspace, resolve_effective_plan_code(workspace))
    workspace.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(workspace)


def update_workspace_billing_from_checkout_session(
    workspace: Workspace,
    session_obj,
    db: Session,
):
    customer_id = getattr(session_obj, "customer", None)
    subscription_id = getattr(session_obj, "subscription", None)
    metadata = getattr(session_obj, "metadata", {}) or {}

    target_plan_code = metadata.get("target_plan_code")

    workspace.billing_provider = "stripe"

    if customer_id:
        workspace.stripe_customer_id = customer_id

    if subscription_id:
        workspace.stripe_subscription_id = subscription_id

    if target_plan_code:
        workspace.plan_code = normalize_plan_code(target_plan_code)

    apply_workspace_plan_limits(workspace, resolve_effective_plan_code(workspace))
    workspace.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(workspace)


def update_workspace_billing_from_paddle_event(
    workspace: Workspace,
    event_data: dict,
    db: Session,
):
    custom_data = event_data.get("custom_data") or {}
    customer_id = (
        event_data.get("customer_id")
        or (event_data.get("customer") or {}).get("id")
        or workspace.paddle_customer_id
    )
    subscription_id = (
        event_data.get("subscription_id")
        or (event_data.get("subscription") or {}).get("id")
        or workspace.paddle_subscription_id
    )
    transaction_id = event_data.get("id") if str(event_data.get("id", "")).startswith("txn_") else None
    price_id = None

    items = event_data.get("items") or []
    if items and isinstance(items, list):
        first_item = items[0] or {}
        price = first_item.get("price") or {}
        price_id = price.get("id") or first_item.get("price_id")

    if customer_id:
        workspace.paddle_customer_id = customer_id
    if subscription_id:
        workspace.paddle_subscription_id = subscription_id
    if transaction_id:
        workspace.paddle_transaction_id = transaction_id
    if price_id:
        workspace.paddle_price_id = price_id

    target_plan_code = custom_data.get("target_plan_code")
    if target_plan_code:
        workspace.plan_code = normalize_plan_code(target_plan_code)

    interval = custom_data.get("billing_cycle")
    if not interval and price_id:
        for key, mapped_price_id in get_paddle_price_catalog().items():
            if mapped_price_id == price_id:
                interval = "annual" if key.endswith("_annual") else "monthly"
                break

    status = str(event_data.get("status") or "").strip().lower()
    subscription_status = (
        (event_data.get("subscription") or {}).get("status")
        or event_data.get("status")
        or "active"
    )
    workspace.billing_provider = "paddle"

    if status in {"completed", "paid", "billed"}:
        workspace.billing_status = "active"
    else:
        workspace.billing_status = map_paddle_subscription_status(subscription_status)

    next_billed_at = (
        event_data.get("next_billed_at")
        or ((event_data.get("current_billing_period") or {}).get("ends_at"))
        or ((event_data.get("billing_period") or {}).get("ends_at"))
    )
    parsed_period_end = parse_iso_datetime(next_billed_at)
    if parsed_period_end:
        workspace.subscription_current_period_end = parsed_period_end
    elif interval:
        workspace.subscription_current_period_end = fallback_period_end_for_cycle(interval)

    apply_workspace_plan_limits(workspace, resolve_effective_plan_code(workspace))
    workspace.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(workspace)


def find_workspace_for_subscription(db: Session, subscription):
    metadata = getattr(subscription, "metadata", {}) or {}
    workspace_id = metadata.get("workspace_id")

    if workspace_id:
        workspace = db.query(Workspace).filter(Workspace.id == int(workspace_id)).first()
        if workspace:
            return workspace

    customer_id = getattr(subscription, "customer", None)
    if customer_id:
        workspace = db.query(Workspace).filter(Workspace.stripe_customer_id == customer_id).first()
        if workspace:
            return workspace

    subscription_id = getattr(subscription, "id", None)
    if subscription_id:
        workspace = db.query(Workspace).filter(Workspace.stripe_subscription_id == subscription_id).first()
        if workspace:
            return workspace

    return None


def find_workspace_for_checkout_session(db: Session, session_obj):
    metadata = getattr(session_obj, "metadata", {}) or {}
    workspace_id = metadata.get("workspace_id")

    if workspace_id:
        workspace = db.query(Workspace).filter(Workspace.id == int(workspace_id)).first()
        if workspace:
            return workspace

    customer_id = getattr(session_obj, "customer", None)
    if customer_id:
        workspace = db.query(Workspace).filter(Workspace.stripe_customer_id == customer_id).first()
        if workspace:
            return workspace

    return None


def find_workspace_for_invoice(db: Session, invoice_obj):
    customer_id = invoice_obj.get("customer")
    subscription_id = invoice_obj.get("subscription")

    workspace = None
    if customer_id:
        workspace = db.query(Workspace).filter(Workspace.stripe_customer_id == customer_id).first()

    if not workspace and subscription_id:
        workspace = db.query(Workspace).filter(Workspace.stripe_subscription_id == subscription_id).first()

    return workspace


def find_workspace_for_paddle_data(db: Session, event_data: dict):
    custom_data = event_data.get("custom_data") or {}
    workspace_id = custom_data.get("workspace_id")

    if workspace_id:
        workspace = db.query(Workspace).filter(Workspace.id == int(workspace_id)).first()
        if workspace:
            return workspace

    customer_id = event_data.get("customer_id") or (event_data.get("customer") or {}).get("id")
    if customer_id:
        workspace = db.query(Workspace).filter(Workspace.paddle_customer_id == customer_id).first()
        if workspace:
            return workspace

    subscription_id = event_data.get("subscription_id") or (event_data.get("subscription") or {}).get("id")
    if subscription_id:
        workspace = db.query(Workspace).filter(Workspace.paddle_subscription_id == subscription_id).first()
        if workspace:
            return workspace

    transaction_id = event_data.get("id")
    if transaction_id and str(transaction_id).startswith("txn_"):
        workspace = db.query(Workspace).filter(Workspace.paddle_transaction_id == transaction_id).first()
        if workspace:
            return workspace

    return None


def sync_workspace_from_checkout_session_id(
    workspace: Workspace,
    session_id: str,
    db: Session,
) -> tuple[bool, str | None]:
    ok, config_error = configure_stripe()
    if not ok:
        return False, config_error

    if not session_id or not session_id.strip():
        return False, "Checkout session id is required."

    try:
        session_obj = stripe.checkout.Session.retrieve(session_id.strip())
    except Exception as exc:
        return False, f"Stripe checkout session retrieval failed: {exc}"

    session_workspace = find_workspace_for_checkout_session(db, session_obj)
    if session_workspace and session_workspace.id != workspace.id:
        return False, "Checkout session does not belong to this workspace."

    update_workspace_billing_from_checkout_session(workspace, session_obj, db)

    subscription_id = getattr(session_obj, "subscription", None)
    if subscription_id:
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            update_workspace_billing_from_subscription(workspace, subscription, db)
        except Exception:
            pass

    return True, None


def paddle_verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    secret = str(getattr(settings, "PADDLE_WEBHOOK_SECRET", "") or "").strip()
    if not secret:
        return True

    if not signature_header:
        return False

    try:
        parts = {}
        for item in signature_header.split(";"):
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            parts[key.strip()] = value.strip()

        ts = parts.get("ts")
        provided_h1 = parts.get("h1")
        if not ts or not provided_h1:
            return False

        signed_payload = f"{ts}:{raw_body.decode('utf-8')}".encode("utf-8")
        expected = hmac.new(
            secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, provided_h1)
    except Exception:
        return False


@router.get("/workspaces/{workspace_id}/billing-foundation")
def get_workspace_billing_foundation(
    workspace_id: int,
    checkout_session_id: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        return {"detail": "Workspace not found"}

    membership = require_workspace_member(workspace_id, current_user, db)
    if not membership:
        return {"detail": "User is not a member of this workspace"}

    if checkout_session_id and stripe_is_ready():
        sync_workspace_from_checkout_session_id(workspace, checkout_session_id, db)
        db.refresh(workspace)

    current_plan = get_plan_definition(workspace.plan_code)
    manual_payment_details = get_manual_payment_details()
    configured_plan_code = normalize_plan_code(workspace.plan_code)
    effective_plan_code = resolve_effective_plan_code(workspace)
    apply_workspace_plan_limits(workspace, effective_plan_code)
    db.commit()
    db.refresh(workspace)
    billing_status = normalize_billing_status(workspace.billing_status)

    active_provider = get_active_billing_provider(workspace)
    provider_label = get_billing_provider_display_label(active_provider)
    manual_visible = should_expose_manual_billing(workspace)

    checkout_mode = (
        "paddle_checkout_ready"
        if paddle_is_ready()
        else "stripe_checkout_ready"
        if stripe_is_ready()
        else "manual_billing_ready"
        if manual_billing_is_ready()
        else "placeholder_until_checkout"
    )

    return {
        "workspace_id": workspace.id,
        "plan_code": configured_plan_code,
        "plan_name": current_plan["name"],
        "effective_plan_code": effective_plan_code,
        "billing_status": billing_status,
        "billing_status_is_paid": is_paid_billing_status(billing_status),
        "plan_mismatch": configured_plan_code != effective_plan_code,
        "billing_email": workspace.billing_email,
        "stripe_customer_id": workspace.stripe_customer_id,
        "stripe_subscription_id": workspace.stripe_subscription_id,
        "paddle_customer_id": workspace.paddle_customer_id,
        "paddle_subscription_id": workspace.paddle_subscription_id,
        "paddle_transaction_id": workspace.paddle_transaction_id,
        "paddle_price_id": workspace.paddle_price_id,
        "billing_provider": workspace.billing_provider,
        "active_billing_provider": active_provider,
        "billing_provider_label": provider_label,
        "provider_customer_id": get_provider_customer_id(workspace, active_provider),
        "provider_subscription_id": get_provider_subscription_id(workspace, active_provider),
        "provider_environment": (
            get_paddle_environment() if active_provider == "paddle" else "live"
        ),
        "manual_billing_visible": manual_visible,
        "subscription_current_period_end": (
            workspace.subscription_current_period_end.isoformat()
            if workspace.subscription_current_period_end
            else None
        ),
        "prices": {
            "monthly_price_usd": current_plan["billing"]["monthly_price_usd"],
            "annual_price_usd": current_plan["billing"]["annual_price_usd"],
        },
        "stripe_ready": {
            "has_customer_id": bool(workspace.stripe_customer_id),
            "has_subscription_id": bool(workspace.stripe_subscription_id),
            "integration_status": "fallback_only",
            "billing_enabled": bool(getattr(settings, "STRIPE_BILLING_ENABLED", False)),
            "secret_key_configured": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.strip()),
            "package_installed": stripe is not None,
        },
        "paddle_ready": {
            "enabled": bool(getattr(settings, "PADDLE_BILLING_ENABLED", False)),
            "api_key_configured": bool(
                getattr(settings, "PADDLE_API_KEY", None) and str(settings.PADDLE_API_KEY).strip()
            ),
            "webhook_secret_configured": bool(
                getattr(settings, "PADDLE_WEBHOOK_SECRET", None) and str(settings.PADDLE_WEBHOOK_SECRET).strip()
            ),
            "has_customer_id": bool(workspace.paddle_customer_id),
            "has_subscription_id": bool(workspace.paddle_subscription_id),
            "price_catalog_count": len([v for v in get_paddle_price_catalog().values() if v]),
            "environment": get_paddle_environment(),
        },
        "manual_billing": {
            "enabled": manual_payment_details["enabled"],
            "ready": manual_billing_is_ready(),
            "visible": manual_visible,
            "payment_method": manual_payment_details["payment_method"],
        },
        "manual_payment_details": manual_payment_details if manual_visible else None,
        "checkout_state": {
            "can_start_checkout": True,
            "mode": checkout_mode,
            "portal_available": bool(workspace.paddle_subscription_id or workspace.stripe_customer_id),
        },
    }


@router.post("/workspaces/{workspace_id}/checkout")
def create_billing_checkout_session(
    workspace_id: int,
    payload: BillingCheckoutPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace, access_error = get_workspace_for_owner_access(workspace_id, db, current_user)
    if not workspace:
        return {
            "mode": "access_error",
            "checkout_url": None,
            "url": None,
            "workspace_id": workspace_id,
            "message": access_error or "Workspace access failed.",
        }

    current_plan_code = normalize_plan_code(workspace.plan_code)
    resolved_plan_code = normalize_plan_code(payload.plan_code)
    billing_cycle = normalize_billing_cycle(payload.billing_cycle)
    checkout_intent = checkout_intent_for_target_plan(workspace, resolved_plan_code)

    if resolved_plan_code == "sandbox":
        workspace.plan_code = "sandbox"
        workspace.billing_provider = None
        workspace.billing_status = "inactive"
        workspace.subscription_current_period_end = None
        apply_workspace_plan_limits(workspace, "sandbox")
        workspace.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(workspace)

        return {
            "mode": "sandbox_activation",
            "checkout_url": None,
            "url": None,
            "workspace_id": workspace.id,
            "current_plan_code": current_plan_code,
            "target_plan_code": resolved_plan_code,
            "billing_cycle": billing_cycle,
            "checkout_intent": "sandbox_activation",
            "message": "Sandbox environment activated. No checkout is required for this plan.",
        }

    if not can_start_checkout_for_target_plan(workspace, resolved_plan_code):
        return {
            "mode": "no_op_same_plan",
            "checkout_url": None,
            "url": None,
            "workspace_id": workspace.id,
            "current_plan_code": current_plan_code,
            "target_plan_code": resolved_plan_code,
            "billing_cycle": billing_cycle,
            "checkout_intent": checkout_intent,
            "message": "Selected plan already matches the active workspace plan posture.",
        }

    

    if paddle_is_ready():
        paddle_price_id = get_paddle_price_id(resolved_plan_code, billing_cycle)
        if not paddle_price_id:
            return {
                "mode": "paddle_price_missing",
                "checkout_url": None,
                "url": None,
                "workspace_id": workspace.id,
                "current_plan_code": current_plan_code,
                "target_plan_code": resolved_plan_code,
                "billing_cycle": billing_cycle,
                "checkout_intent": checkout_intent,
                "message": f"No Paddle price id is mapped for {resolved_plan_code} ({billing_cycle}).",
            }

        payload_data = {
            "items": [
                {
                    "price_id": paddle_price_id,
                    "quantity": 1,
                }
            ],
            "custom_data": {
                "workspace_id": str(workspace.id),
                "workspace_name": workspace.name,
                "owner_user_id": str(current_user.id),
                "target_plan_code": resolved_plan_code,
                "billing_cycle": billing_cycle,
                "checkout_intent": checkout_intent,
            },
            "checkout": {
                "success_url": f"{get_frontend_base_url()}/workspace/{workspace.id}/settings?checkout=success",
                "cancel_url": f"{get_frontend_base_url()}/workspace/{workspace.id}/settings?checkout=cancelled"
            }
        }

        paddle_response, paddle_error = paddle_request("POST", "/transactions", payload_data)
        if paddle_error:
            return {
                "mode": "paddle_checkout_error",
                "checkout_url": None,
                "url": None,
                "workspace_id": workspace.id,
                "current_plan_code": current_plan_code,
                "target_plan_code": resolved_plan_code,
                "billing_cycle": billing_cycle,
                "checkout_intent": checkout_intent,
                "message": paddle_error,
                "diagnostics": {
                    "paddle_enabled": bool(getattr(settings, "PADDLE_BILLING_ENABLED", False)),
                    "api_key_configured": bool(
                        getattr(settings, "PADDLE_API_KEY", None) and str(settings.PADDLE_API_KEY).strip()
                    ),
                    "paddle_price_id": paddle_price_id,
                },
            }

        data = (paddle_response or {}).get("data") or {}
        checkout_data = data.get("checkout") or {}
        checkout_url = checkout_data.get("url") or data.get("checkout_url")

        if not checkout_url:
            return {
                "mode": "paddle_checkout_error",
                "checkout_url": None,
                "url": None,
                "workspace_id": workspace.id,
                "current_plan_code": current_plan_code,
                "target_plan_code": resolved_plan_code,
                "billing_cycle": billing_cycle,
                "checkout_intent": checkout_intent,
                "message": "Paddle transaction was created but no checkout URL was returned.",
                "diagnostics": {
                    "paddle_transaction_id": data.get("id"),
                    "paddle_price_id": paddle_price_id,
                },
            }

        workspace.billing_provider = "paddle"
        workspace.paddle_transaction_id = data.get("id")
        workspace.paddle_price_id = paddle_price_id
        workspace.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(workspace)

        return {
            "mode": "paddle_checkout",
            "checkout_url": checkout_url,
            "url": checkout_url,
            "transaction_id": data.get("id"),
            "workspace_id": workspace.id,
            "current_plan_code": current_plan_code,
            "target_plan_code": resolved_plan_code,
            "billing_cycle": billing_cycle,
            "checkout_intent": checkout_intent,
            "paddle_price_id": paddle_price_id,
            "message": "Paddle checkout created successfully.",
        }

    price_lookup_key = get_price_lookup_key(resolved_plan_code, billing_cycle)

    if stripe_is_ready():
        customer, customer_error = get_or_create_stripe_customer(workspace, current_user, db)
        if customer_error:
            return {
                "mode": "stripe_customer_error",
                "checkout_url": None,
                "url": None,
                "workspace_id": workspace.id,
                "current_plan_code": current_plan_code,
                "target_plan_code": resolved_plan_code,
                "billing_cycle": billing_cycle,
                "checkout_intent": checkout_intent,
                "message": customer_error,
                "diagnostics": {
                    "stripe_package_installed": stripe is not None,
                    "billing_enabled": bool(getattr(settings, "STRIPE_BILLING_ENABLED", False)),
                    "secret_key_configured": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.strip()),
                    "price_lookup_key": price_lookup_key,
                },
            }

        price_id, price_error = resolve_stripe_price_id_from_lookup_key(price_lookup_key)
        if price_error:
            return {
                "mode": "stripe_price_missing",
                "checkout_url": None,
                "url": None,
                "workspace_id": workspace.id,
                "current_plan_code": current_plan_code,
                "target_plan_code": resolved_plan_code,
                "billing_cycle": billing_cycle,
                "checkout_intent": checkout_intent,
                "message": price_error,
                "diagnostics": {
                    "stripe_package_installed": stripe is not None,
                    "billing_enabled": bool(getattr(settings, "STRIPE_BILLING_ENABLED", False)),
                    "secret_key_configured": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.strip()),
                    "price_lookup_key": price_lookup_key,
                    "stripe_customer_id": getattr(customer, "id", None),
                },
            }

        try:
            session = stripe.checkout.Session.create(
                mode="subscription",
                success_url=(
                    f"{get_checkout_return_url(workspace.id)}"
                    f"?checkout=success&session_id={{CHECKOUT_SESSION_ID}}"
                ),
                cancel_url=f"{get_checkout_return_url(workspace.id)}?checkout=cancelled",
                line_items=[{"price": price_id, "quantity": 1}],
                metadata={
                    "workspace_id": str(workspace.id),
                    "workspace_name": workspace.name,
                    "owner_user_id": str(current_user.id),
                    "target_plan_code": resolved_plan_code,
                    "billing_cycle": billing_cycle,
                    "checkout_intent": checkout_intent,
                },
                subscription_data={
                    "metadata": {
                        "workspace_id": str(workspace.id),
                        "workspace_name": workspace.name,
                        "owner_user_id": str(current_user.id),
                        "target_plan_code": resolved_plan_code,
                        "billing_cycle": billing_cycle,
                        "checkout_intent": checkout_intent,
                    }
                },
                customer=getattr(customer, "id", None),
                customer_update={"address": "auto", "name": "auto"},
                allow_promotion_codes=True,
            )
        except Exception as exc:
            return {
                "mode": "stripe_checkout_error",
                "checkout_url": None,
                "url": None,
                "workspace_id": workspace.id,
                "current_plan_code": current_plan_code,
                "target_plan_code": resolved_plan_code,
                "billing_cycle": billing_cycle,
                "checkout_intent": checkout_intent,
                "message": f"Stripe checkout session creation failed: {exc}",
                "diagnostics": {
                    "stripe_package_installed": stripe is not None,
                    "billing_enabled": bool(getattr(settings, "STRIPE_BILLING_ENABLED", False)),
                    "secret_key_configured": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.strip()),
                    "price_lookup_key": price_lookup_key,
                    "stripe_price_id": price_id,
                    "stripe_customer_id": getattr(customer, "id", None),
                },
            }

        workspace.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(workspace)

        return {
            "mode": "stripe_checkout",
            "checkout_url": getattr(session, "url", None),
            "url": getattr(session, "url", None),
            "session_id": getattr(session, "id", None),
            "workspace_id": workspace.id,
            "current_plan_code": current_plan_code,
            "target_plan_code": resolved_plan_code,
            "billing_cycle": billing_cycle,
            "checkout_intent": checkout_intent,
            "stripe_customer_id": workspace.stripe_customer_id,
            "stripe_price_id": price_id,
            "stripe_price_lookup_key": price_lookup_key,
            "message": "Stripe checkout session created successfully.",
        }

    if manual_billing_is_ready():
        workspace.billing_provider = "manual"
        workspace.billing_status = "pending_manual_review"
        workspace.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(workspace)

        return {
            "mode": "manual_billing_checkout",
            "checkout_url": None,
            "url": None,
            "workspace_id": workspace.id,
            "current_plan_code": current_plan_code,
            "target_plan_code": resolved_plan_code,
            "billing_cycle": billing_cycle,
            "checkout_intent": checkout_intent,
            "message": (
                f"Manual billing instructions generated for {resolved_plan_code} "
                f"({billing_cycle}). Complete payment using the details shown below, "
                "then confirm manually."
            ),
            "manual_payment_details": get_manual_payment_details(),
            "diagnostics": {
                "stripe_package_installed": stripe is not None,
                "billing_enabled": bool(getattr(settings, "STRIPE_BILLING_ENABLED", False)),
                "secret_key_configured": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY.strip()),
                "price_lookup_key": price_lookup_key,
                "manual_billing_enabled": bool(getattr(settings, "MANUAL_BILLING_ENABLED", False)),
            },
        }

    return {
        "mode": "placeholder_until_checkout",
        "checkout_url": None,
        "url": None,
        "workspace_id": workspace.id,
        "current_plan_code": current_plan_code,
        "target_plan_code": resolved_plan_code,
        "billing_cycle": billing_cycle,
        "checkout_intent": checkout_intent,
        "message": (
            "Checkout foundation is ready, but Paddle, Stripe, and manual billing "
            "are not fully configured yet."
        ),
        "diagnostics": {
            "paddle_enabled": bool(getattr(settings, "PADDLE_BILLING_ENABLED", False)),
            "stripe_package_installed": stripe is not None,
            "stripe_billing_enabled": bool(getattr(settings, "STRIPE_BILLING_ENABLED", False)),
            "manual_billing_enabled": bool(getattr(settings, "MANUAL_BILLING_ENABLED", False)),
        },
    }


@router.post("/workspaces/{workspace_id}/portal")
def create_billing_portal_session(
    workspace_id: int,
    payload: BillingPortalPayload | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace, access_error = get_workspace_for_owner_access(workspace_id, db, current_user)
    if not workspace:
        return {
            "mode": "access_error",
            "portal_url": None,
            "url": None,
            "workspace_id": workspace_id,
            "message": access_error or "Workspace access failed.",
        }


    if paddle_is_ready():
        return {
            "mode": "paddle_portal_pending",
            "portal_url": None,
            "url": None,
            "workspace_id": workspace.id,
            "message": (
                "Paddle checkout automation is active. Customer self-serve portal is not wired yet "
                "in this build. Use support/admin workflow for subscription changes for now."
            ),
        }

    if stripe_is_ready():
        if not workspace.stripe_customer_id:
            return {
                "mode": "portal_unavailable",
                "portal_url": None,
                "url": None,
                "workspace_id": workspace.id,
                "message": "Billing portal is not available yet because this workspace has no Stripe customer connection.",
            }

        ok, config_error = configure_stripe()
        if not ok:
            return {
                "mode": "portal_config_error",
                "portal_url": None,
                "url": None,
                "workspace_id": workspace.id,
                "message": config_error or "Stripe configuration failed.",
            }

        return_url = (
            payload.return_url.strip()
            if payload and payload.return_url and payload.return_url.strip()
            else f"{get_checkout_return_url(workspace.id)}?portal=returned"
        )

        try:
            session = stripe.billing_portal.Session.create(
                customer=workspace.stripe_customer_id,
                return_url=return_url,
            )
        except Exception as exc:
            return {
                "mode": "portal_error",
                "portal_url": None,
                "url": None,
                "workspace_id": workspace.id,
                "message": f"Stripe billing portal session creation failed: {exc}",
            }

        return {
            "mode": "stripe_portal",
            "portal_url": getattr(session, "url", None),
            "url": getattr(session, "url", None),
            "workspace_id": workspace.id,
            "created_at": datetime.utcnow().isoformat(),
        }

    if manual_billing_is_ready():
        return {
            "mode": "manual_billing_portal",
            "portal_url": None,
            "url": None,
            "workspace_id": workspace.id,
            "message": "Manual billing mode is active. Use the payment instructions below and contact support/admin for plan changes.",
            "manual_payment_details": get_manual_payment_details(),
        }

    return {
        "mode": "portal_placeholder",
        "portal_url": None,
        "url": None,
        "workspace_id": workspace.id,
        "message": "Billing portal foundation is ready, but no active portal flow is configured.",
    }


@router.post("/paddle/webhook")
async def paddle_webhook(request: Request):
    body = await request.body()

    secret = settings.PADDLE_WEBHOOK_SECRET
    signature = request.headers.get("paddle-signature")

    if not signature or not verify_paddle_signature(body, signature, secret):
        return {"status": "invalid signature"}

    data = await request.json()

    # 👉 continue your existing logic here
    # e.g. subscription activated, updated, etc.

    return {"status": "ok"}

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        return {
            "received": False,
            "mode": "invalid_payload",
            "message": "Invalid Paddle webhook payload.",
        }

    event_type = payload.get("event_type")
    event_data = (payload.get("data") or {}) if isinstance(payload, dict) else {}

    try:
        workspace = find_workspace_for_paddle_data(db, event_data)
        if not workspace:
            return {
                "received": True,
                "event_type": event_type,
                "message": "No matching workspace found for Paddle event.",
            }

        if event_type in {
            "transaction.completed",
            "transaction.paid",
            "subscription.created",
            "subscription.updated",
            "subscription.activated",
            "subscription.resumed",
            "subscription.canceled",
            "subscription.paused",
            "subscription.past_due",
        }:
            update_workspace_billing_from_paddle_event(workspace, event_data, db)

    except Exception as exc:
        return {
            "received": False,
            "mode": "webhook_processing_failed",
            "event_type": event_type,
            "message": f"Paddle webhook processing failed: {exc}",
        }

    return {
        "received": True,
        "event_type": event_type,
    }


@router.post("/stripe/webhooks")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: Session = Depends(get_db),
):
    if stripe is None:
        return {
            "received": False,
            "mode": "stripe_package_missing",
            "message": "Stripe package is not installed.",
        }

    payload = await request.body()

    if not settings.STRIPE_WEBHOOK_SECRET or not settings.STRIPE_WEBHOOK_SECRET.strip():
        return {
            "received": False,
            "mode": "webhook_not_configured",
            "message": "STRIPE_WEBHOOK_SECRET is not configured.",
        }

    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_SECRET_KEY.strip():
        return {
            "received": False,
            "mode": "stripe_secret_not_configured",
            "message": "STRIPE_SECRET_KEY is not configured.",
        }

    if not stripe_signature:
        return {
            "received": False,
            "mode": "missing_signature",
            "message": "Missing Stripe-Signature header.",
        }

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=settings.STRIPE_WEBHOOK_SECRET.strip(),
        )
    except ValueError:
        return {
            "received": False,
            "mode": "invalid_payload",
            "message": "Invalid webhook payload.",
        }
    except Exception as exc:
        return {
            "received": False,
            "mode": "signature_verification_failed",
            "message": f"Webhook signature verification failed: {exc}",
        }

    event_type = event.get("type")
    data_object = (event.get("data") or {}).get("object") or {}

    try:
        if event_type == "checkout.session.completed":
            workspace = find_workspace_for_checkout_session(db, data_object)
            if workspace:
                update_workspace_billing_from_checkout_session(workspace, data_object, db)

                subscription_id = getattr(data_object, "subscription", None) or data_object.get("subscription")
                if subscription_id:
                    try:
                        subscription = stripe.Subscription.retrieve(subscription_id)
                        update_workspace_billing_from_subscription(workspace, subscription, db)
                    except Exception:
                        pass

        elif event_type in {
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        }:
            workspace = find_workspace_for_subscription(db, data_object)
            if workspace:
                update_workspace_billing_from_subscription(workspace, data_object, db)

        elif event_type == "invoice.paid":
            workspace = find_workspace_for_invoice(db, data_object)
            if workspace:
                workspace.billing_provider = "stripe"
                workspace.billing_status = "active"
                workspace.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(workspace)

        elif event_type == "invoice.payment_failed":
            workspace = find_workspace_for_invoice(db, data_object)
            if workspace:
                workspace.billing_provider = "stripe"
                workspace.billing_status = "past_due"
                workspace.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(workspace)

    except Exception as exc:
        return {
            "received": False,
            "mode": "webhook_processing_failed",
            "event_type": event_type,
            "message": f"Webhook processing failed: {exc}",
        }

    return {
        "received": True,
        "event_type": event_type,
    }

from fastapi import Request
import json


@router.post("/webhook/paddle")
async def paddle_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.body()
        payload = json.loads(body)

        event_type = payload.get("event_type")
        data = payload.get("data", {})

        # ----------------------------
        # SUBSCRIPTION CREATED / PAID
        # ----------------------------
        if event_type in ["subscription.created", "subscription.updated"]:
            customer_id = data.get("customer_id")
            subscription_id = data.get("id")
            status = data.get("status")
            price_id = data.get("price_id")

            workspace = (
                db.query(Workspace)
                .filter(Workspace.paddle_customer_id == customer_id)
                .first()
            )

            if workspace:
                workspace.paddle_subscription_id = subscription_id
                workspace.paddle_price_id = price_id

                if status in ["active", "trialing"]:
                    workspace.billing_status = "active"
                else:
                    workspace.billing_status = "inactive"

                db.commit()

        # ----------------------------
        # PAYMENT SUCCESS
        # ----------------------------
        if event_type == "transaction.completed":
            customer_id = data.get("customer_id")
            transaction_id = data.get("id")

            workspace = (
                db.query(Workspace)
                .filter(Workspace.paddle_customer_id == customer_id)
                .first()
            )

            if workspace:
                workspace.paddle_transaction_id = transaction_id
                workspace.billing_status = "active"
                db.commit()

        return {"status": "ok"}

    except Exception as e:
        print("Webhook error:", str(e))
        return {"status": "error"}


@router.get("/workspaces/{workspace_id}/usage")
def get_workspace_usage_adapter(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return {
        "workspace_id": workspace.id,
        "trade_limit": getattr(workspace, "trade_limit", 0),
        "trades_used": getattr(workspace, "trades_consumed_count", 0),
        "claim_limit": getattr(workspace, "claim_limit", 0),
    }   


@router.get("/workspaces/{workspace_id}/dashboard")
def get_workspace_dashboard(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    trade_count = db.query(Trade).filter(Trade.workspace_id == workspace_id).count()

    return {
        "workspace_id": workspace.id,
        "workspace_name": workspace.name,
        "member_count": workspace.member_limit,
        "trade_count": trade_count,
        "claim_count": getattr(workspace, "claim_limit", 0),
    }