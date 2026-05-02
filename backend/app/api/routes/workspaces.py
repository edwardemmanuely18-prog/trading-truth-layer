from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership
from app.services.audit_service import log_audit_event

from app.models.trade import Trade
from app.models.workspace import Workspace
from fastapi import HTTPException

router = APIRouter()


class CreateWorkspacePayload(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class UpdateWorkspaceSettingsPayload(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    billing_email: str | None = Field(default=None, max_length=255)


class UpdateWorkspaceMemberRolePayload(BaseModel):
    role: str = Field(min_length=1, max_length=50)


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
        raise HTTPException(status_code=403, detail="User is not a member of this workspace")

    return membership


def require_workspace_owner(workspace_id: int, current_user: User, db: Session):
    membership = require_workspace_member(workspace_id, current_user, db)
    if membership.role != "owner":
        raise HTTPException(status_code=403, detail="Owner role required for this workspace")
    return membership


def serialize_workspace_member(membership: WorkspaceMembership, user: User):
    return {
        "workspace_id": membership.workspace_id,
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "global_role": user.role,
        "workspace_role": membership.role,
    }


def normalize_plan_code(plan_code: str | None) -> str:
    allowed = {"sandbox", "starter", "pro", "growth", "business"}
    value = str(plan_code or "").strip().lower()
    return value if value in allowed else "starter"


def normalize_billing_status(status: str | None) -> str:
    allowed = {
        "inactive",
        "active",
        "trialing",
        "past_due",
        "canceled",
        "unpaid",
        "pending_manual_review",
    }
    value = str(status or "").strip().lower()
    return value if value in allowed else "inactive"


def normalize_workspace_role(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    allowed_roles = {"owner", "operator", "member", "auditor"}
    return normalized if normalized in allowed_roles else "member"


def get_plan_order() -> list[str]:
    return ["sandbox", "starter", "pro", "growth", "business"]


def get_plan_catalog():
    return [
        {
            "code": "sandbox",
            "name": "Sandbox",
            "description": "Controlled evaluation environment for product proof and safe pre-billing exploration.",
            "limits": {
                "claim_limit": 2,
                "trade_limit": 200,
                "member_limit": 2,
                "storage_limit_mb": 100,
            },
            "recommended_for": [
                "internal demos",
                "early product proof",
                "controlled evaluation",
            ],
            "billing": {
                "monthly_price_usd": 0,
                "annual_price_usd": 0,
                "currency": "USD",
                "billing_interval": "none",
                "stripe_price_lookup_key_monthly": None,
                "stripe_price_lookup_key_annual": None,
            },
            "public_price_hint": "sandbox_controlled_evaluation",
        },
        {
            "code": "starter",
            "name": "Starter",
            "description": "Entry plan for early operators validating claim workflows.",
            "limits": {
                "claim_limit": 5,
                "trade_limit": 1000,
                "member_limit": 3,
                "storage_limit_mb": 500,
            },
            "recommended_for": [
                "solo traders",
                "small verification pilots",
                "early workspace setup",
            ],
            "billing": {
                "monthly_price_usd": 19,
                "annual_price_usd": 190,
                "currency": "USD",
                "billing_interval": "monthly_or_annual",
                "stripe_price_lookup_key_monthly": "ttl_starter_monthly",
                "stripe_price_lookup_key_annual": "ttl_starter_annual",
            },
            "public_price_hint": "starter_placeholder",
        },
        {
            "code": "pro",
            "name": "Pro",
            "description": "Higher limits for serious traders and small commercial operators.",
            "limits": {
                "claim_limit": 25,
                "trade_limit": 10000,
                "member_limit": 10,
                "storage_limit_mb": 5000,
            },
            "recommended_for": [
                "serious traders",
                "educators",
                "small paid communities",
            ],
            "billing": {
                "monthly_price_usd": 79,
                "annual_price_usd": 790,
                "currency": "USD",
                "billing_interval": "monthly_or_annual",
                "stripe_price_lookup_key_monthly": "ttl_pro_monthly",
                "stripe_price_lookup_key_annual": "ttl_pro_annual",
            },
            "public_price_hint": "pro_placeholder",
        },
        {
            "code": "growth",
            "name": "Growth",
            "description": "Operational tier for teams running multiple verification surfaces.",
            "limits": {
                "claim_limit": 100,
                "trade_limit": 100000,
                "member_limit": 50,
                "storage_limit_mb": 25000,
            },
            "recommended_for": [
                "signal groups",
                "prop-style operators",
                "growing businesses",
            ],
            "billing": {
                "monthly_price_usd": 249,
                "annual_price_usd": 2490,
                "currency": "USD",
                "billing_interval": "monthly_or_annual",
                "stripe_price_lookup_key_monthly": "ttl_growth_monthly",
                "stripe_price_lookup_key_annual": "ttl_growth_annual",
            },
            "public_price_hint": "growth_placeholder",
        },
        {
            "code": "business",
            "name": "Business",
            "description": "High-capacity tier for institutional and infrastructure use cases.",
            "limits": {
                "claim_limit": 500,
                "trade_limit": 1000000,
                "member_limit": 250,
                "storage_limit_mb": 100000,
            },
            "recommended_for": [
                "funds",
                "institutions",
                "B2B verification operations",
            ],
            "billing": {
                "monthly_price_usd": 999,
                "annual_price_usd": 9990,
                "currency": "USD",
                "billing_interval": "monthly_or_annual",
                "stripe_price_lookup_key_monthly": "ttl_business_monthly",
                "stripe_price_lookup_key_annual": "ttl_business_annual",
            },
            "public_price_hint": "business_placeholder",
        },
    ]


def get_plan_definition(plan_code: str | None):
    normalized = normalize_plan_code(plan_code)
    for plan in get_plan_catalog():
        if plan["code"] == normalized:
            return plan
    return get_plan_catalog()[0]


def is_paid_billing_status(status: str | None) -> bool:
    normalized = normalize_billing_status(status)
    return normalized in {"active", "trialing"}


def resolve_effective_plan_code(workspace: Workspace) -> str:
    configured_plan = normalize_plan_code(workspace.plan_code)
    billing_status = normalize_billing_status(workspace.billing_status)

    # 🔒 HARD OVERRIDE
    if configured_plan == "sandbox":
        return "sandbox"

    if configured_plan == "starter":
        return "starter"

    if is_paid_billing_status(billing_status):
        return configured_plan

    return "starter"


def resolve_effective_plan_definition(workspace: Workspace):
    return get_plan_definition(resolve_effective_plan_code(workspace))


def workspace_limit_snapshot(workspace: Workspace):
    effective_plan = resolve_effective_plan_definition(workspace)

    return {
        "claim_limit": effective_plan["limits"]["claim_limit"],
        "trade_limit": effective_plan["limits"]["trade_limit"],
        "member_limit": effective_plan["limits"]["member_limit"],
        "storage_limit_mb": effective_plan["limits"]["storage_limit_mb"],
    }


def build_plan_governance_state(workspace: Workspace):
    configured_plan_code = normalize_plan_code(workspace.plan_code)
    effective_plan_code = resolve_effective_plan_code(workspace)
    billing_status = normalize_billing_status(workspace.billing_status)

    plan_mismatch = configured_plan_code != effective_plan_code
    paid_access_active = is_paid_billing_status(billing_status)

    if configured_plan_code == "sandbox":
        reason = "sandbox_evaluation"
        message = (
            "Workspace is operating in the controlled evaluation environment. "
            "Sandbox limits are active and no paid billing is required for this tier."
        )
    elif plan_mismatch and configured_plan_code != "starter":
        if billing_status == "pending_manual_review":
            reason = "pending_payment_review"
            message = (
                "Workspace is assigned to a paid plan target, but paid entitlements are not active "
                "until manual billing review is approved."
            )
        else:
            reason = "billing_inactive_fallback"
            message = (
                "Workspace is assigned to a paid plan target, but paid entitlements are inactive. "
                "Effective workspace limits fall back to Starter until billing becomes active."
            )
    else:
        reason = "ok"
        message = "Effective entitlements are aligned with current billing state."

    return {
        "configured_plan_code": configured_plan_code,
        "effective_plan_code": effective_plan_code,
        "billing_status": billing_status,
        "paid_access_active": paid_access_active,
        "plan_mismatch": plan_mismatch,
        "reason": reason,
        "message": message,
    }


def serialize_workspace_settings(workspace: Workspace):
    configured_plan = normalize_plan_code(workspace.plan_code)
    normalized_billing = normalize_billing_status(workspace.billing_status)
    effective_plan = resolve_effective_plan_definition(workspace)
    governance_state = build_plan_governance_state(workspace)
    limits = {
        "claim_limit": effective_plan["limits"]["claim_limit"],
        "trade_limit": effective_plan["limits"]["trade_limit"],
        "member_limit": effective_plan["limits"]["member_limit"],
        "storage_limit_mb": effective_plan["limits"]["storage_limit_mb"],
    }

    configured_plan_definition = get_plan_definition(configured_plan)

    return {
        "workspace_id": workspace.id,
        "name": workspace.name,
        "description": workspace.description,
        "billing_email": workspace.billing_email,
        "plan_code": configured_plan,
        "billing_status": normalized_billing,
        "stripe_customer_id": workspace.stripe_customer_id,
        "stripe_subscription_id": workspace.stripe_subscription_id,
        "subscription_current_period_end": (
            workspace.subscription_current_period_end.isoformat()
            if workspace.subscription_current_period_end
            else None
        ),
        "limits": limits,
        "plan_detail": {
            "code": configured_plan_definition["code"],
            "name": configured_plan_definition["name"],
            "description": configured_plan_definition["description"],
            "recommended_for": configured_plan_definition["recommended_for"],
            "billing": configured_plan_definition["billing"],
        },
        "effective_plan_code": governance_state["effective_plan_code"],
        "effective_plan_detail": {
            "code": effective_plan["code"],
            "name": effective_plan["name"],
            "description": effective_plan["description"],
            "recommended_for": effective_plan["recommended_for"],
            "billing": effective_plan["billing"],
        },
        "effective_limits": limits,
        "plan_governance": governance_state,
        "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
        "updated_at": workspace.updated_at.isoformat() if workspace.updated_at else None,
    }


def usage_row_for_plan(plan_code: str, used: int, dimension: str):
    plan = get_plan_definition(plan_code)

    limit_key_map = {
        "members": "member_limit",
        "trades": "trade_limit",
        "active_trades": "trade_limit",
        "claims": "claim_limit",
        "storage_mb": "storage_limit_mb",
    }

    limit_key = limit_key_map[dimension]
    limit = plan["limits"][limit_key]

    if not limit or limit <= 0:
        ratio = None
        status = "unlimited"
    else:
        ratio = round(used / limit, 4)
        if used > limit:
            status = "over_limit"
        elif used == limit:
            status = "at_limit"
        elif used / limit >= 0.8:
            status = "near_limit"
        else:
            status = "ok"

    return {
        "used": used,
        "limit": limit,
        "ratio": ratio,
        "status": status,
    }


def build_upgrade_recommendation(
    configured_plan_code: str,
    effective_plan_code: str,
    usage_summary: dict,
    plan_mismatch: bool = False,
):
    current_order = get_plan_order()
    configured_normalized = normalize_plan_code(configured_plan_code)
    effective_normalized = normalize_plan_code(effective_plan_code)

    configured_index = current_order.index(configured_normalized)
    effective_index = current_order.index(effective_normalized)

    configured_breached_dimensions = []
    configured_near_limit_dimensions = []

    for key, row in usage_summary.items():
        if key == "active_trades":
            continue
        configured_row = usage_row_for_plan(configured_normalized, row["used"], key)

        if configured_row["status"] == "over_limit":
            configured_breached_dimensions.append(key)
        elif configured_row["status"] in {"at_limit", "near_limit"}:
            configured_near_limit_dimensions.append(key)

    configured_has_breaches = len(configured_breached_dimensions) > 0
    configured_has_near_limits = len(configured_near_limit_dimensions) > 0

    if plan_mismatch and configured_index > effective_index:
        if not configured_has_breaches and not configured_has_near_limits:
            configured_plan = get_plan_definition(configured_normalized)
            return {
                "current_plan_code": configured_normalized,
                "effective_plan_code": effective_normalized,
                "recommendation_basis_plan_code": configured_normalized,
                "recommended_plan_code": configured_normalized,
                "recommended_plan_name": configured_plan["name"],
                "recommended_plan_is_distinct": False,
                "upgrade_required_now": False,
                "upgrade_recommended_soon": False,
                "billing_activation_recommended": configured_normalized not in {"sandbox", "starter"},
                "already_at_highest_tier": configured_index >= len(current_order) - 1,
                "breached_dimensions": [],
                "near_limit_dimensions": [],
            }

        if configured_has_near_limits and not configured_has_breaches:
            if configured_index < len(current_order) - 1:
                recommended_index = configured_index + 1
                recommended_plan = get_plan_definition(current_order[recommended_index])
                return {
                    "current_plan_code": configured_normalized,
                    "effective_plan_code": effective_normalized,
                    "recommendation_basis_plan_code": configured_normalized,
                    "recommended_plan_code": recommended_plan["code"],
                    "recommended_plan_name": recommended_plan["name"],
                    "recommended_plan_is_distinct": True,
                    "upgrade_required_now": False,
                    "upgrade_recommended_soon": True,
                    "billing_activation_recommended": configured_normalized not in {"sandbox", "starter"},
                    "already_at_highest_tier": False,
                    "breached_dimensions": [],
                    "near_limit_dimensions": configured_near_limit_dimensions,
                }

            configured_plan = get_plan_definition(configured_normalized)
            return {
                "current_plan_code": configured_normalized,
                "effective_plan_code": effective_normalized,
                "recommendation_basis_plan_code": configured_normalized,
                "recommended_plan_code": configured_plan["code"],
                "recommended_plan_name": configured_plan["name"],
                "recommended_plan_is_distinct": False,
                "upgrade_required_now": False,
                "upgrade_recommended_soon": False,
                "billing_activation_recommended": configured_normalized not in {"sandbox", "starter"},
                "already_at_highest_tier": True,
                "breached_dimensions": [],
                "near_limit_dimensions": configured_near_limit_dimensions,
            }

    current_index = max(configured_index, effective_index)
    current_normalized = current_order[current_index]

    breached_dimensions = []
    near_limit_dimensions = []

    for key, row in usage_summary.items():
        if key == "active_trades":
            continue
        used = row["used"]
        limit = row["limit"]
        ratio = row["ratio"]

        if limit and limit > 0 and used > limit:
            breached_dimensions.append(key)
        elif limit and limit > 0 and ratio is not None and ratio >= 0.8:
            near_limit_dimensions.append(key)

    has_breaches = len(breached_dimensions) > 0
    has_near_limits = len(near_limit_dimensions) > 0
    already_at_highest_tier = current_index >= len(current_order) - 1

    if (has_breaches or has_near_limits) and not already_at_highest_tier:
        recommended_index = current_index + 1
    else:
        recommended_index = current_index

    recommended_plan_code = current_order[recommended_index]
    recommended_plan = get_plan_definition(recommended_plan_code)
    has_distinct_recommendation = recommended_plan_code != current_normalized

    return {
        "current_plan_code": configured_normalized,
        "effective_plan_code": effective_normalized,
        "recommendation_basis_plan_code": current_normalized,
        "recommended_plan_code": recommended_plan_code,
        "recommended_plan_name": recommended_plan["name"],
        "recommended_plan_is_distinct": has_distinct_recommendation,
        "upgrade_required_now": has_breaches and has_distinct_recommendation,
        "upgrade_recommended_soon": (not has_breaches) and has_near_limits and has_distinct_recommendation,
        "billing_activation_recommended": (
            plan_mismatch
            and configured_index > effective_index
            and not has_distinct_recommendation
            and configured_normalized not in {"sandbox", "starter"}
        ),
        "already_at_highest_tier": already_at_highest_tier,
        "breached_dimensions": breached_dimensions,
        "near_limit_dimensions": near_limit_dimensions,

        "billing_activation_recommended": (
            configured_normalized not in {"sandbox", "starter"}
        ),
    }


@router.get("/workspaces")
def list_my_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(WorkspaceMembership, Workspace)
        .join(Workspace, Workspace.id == WorkspaceMembership.workspace_id)
        .filter(WorkspaceMembership.user_id == current_user.id)
        .order_by(Workspace.id.asc())
        .all()
    )

    return [
        {
            "workspace_id": workspace.id,
            "workspace_name": workspace.name,
            "workspace_role": membership.role,
        }
        for membership, workspace in rows
    ]


@router.post("/workspaces")
def create_workspace(
    payload: CreateWorkspacePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = Workspace(
        name=payload.name.strip(),
        plan_code="sandbox",
        billing_status="inactive",
        claim_limit=2,
        trade_limit=200,
        member_limit=2,
        storage_limit_mb=100,
    )
    db.add(workspace)
    db.flush()

    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(membership)

    db.commit()
    db.refresh(workspace)

    return {
        "workspace_id": workspace.id,
        "workspace_name": workspace.name,
        "workspace_role": "owner",
    }


@router.get("/workspaces/{workspace_id}/dashboard")
def get_workspace_dashboard(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_member(workspace_id, current_user, db)

    member_ids = db.query(Trade.member_id).filter(Trade.workspace_id == workspace_id).distinct().all()
    trade_count = db.query(Trade).filter(Trade.workspace_id == workspace_id).count()
    claim_count = db.query(ClaimSchema).filter(ClaimSchema.workspace_id == workspace_id).count()

    return {
        "workspace_id": workspace.id,
        "workspace_name": workspace.name,
        "member_count": len(member_ids),
        "trade_count": trade_count,
        "claim_count": claim_count,
    }


@router.get("/workspaces/{workspace_id}/settings")
def get_workspace_settings(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_member(workspace_id, current_user, db)
    return serialize_workspace_settings(workspace)


@router.patch("/workspaces/{workspace_id}/settings")
def update_workspace_settings(
    workspace_id: int,
    payload: UpdateWorkspaceSettingsPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_owner(workspace_id, current_user, db)

    workspace.name = payload.name.strip()
    workspace.description = (payload.description or "").strip() or None
    workspace.billing_email = (payload.billing_email or "").strip() or None
    workspace.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(workspace)

    return serialize_workspace_settings(workspace)
    


from app.services.metrics_service import get_workspace_trade_metrics

@router.get("/workspaces/{workspace_id}/usage")
def get_workspace_usage(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.workspace import Workspace

    try:
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        require_workspace_member(workspace_id, current_user, db)

        metrics = get_workspace_trade_metrics(db, workspace_id)
        limits = workspace_limit_snapshot(workspace)
        governance_state = build_plan_governance_state(workspace)

        member_count = db.query(WorkspaceMembership).filter(
            WorkspaceMembership.workspace_id == workspace_id
        ).count()

        trade_count = db.query(Trade).filter(
            Trade.workspace_id == workspace_id
        ).count()

        claim_count = db.query(ClaimSchema).filter(
            ClaimSchema.workspace_id == workspace_id
        ).count()

        storage_used_mb = 0

        def ratio(used, limit):
            return round(used / limit, 4) if limit else None

        def status(used, limit):
            if not limit:
                return "unlimited"
            if used > limit:
                return "over_limit"
            if used == limit:
                return "at_limit"
            if used / limit >= 0.8:
                return "near_limit"
            return "ok"

        usage = {
            "members": {
                "used": member_count,
                "limit": limits["member_limit"],
                "ratio": ratio(member_count, limits["member_limit"]),
                "status": status(member_count, limits["member_limit"]),
            },
            "trades": {
                "used": metrics["consumed"],        # 🔒 IMMUTABLE usage
                "limit": limits["trade_limit"],
                "ratio": ratio(metrics["consumed"], limits["trade_limit"]),
                "status": status(metrics["consumed"], limits["trade_limit"]),

                # 👇 ADD THIS FOR UI DISPLAY (OPTIONAL BUT IMPORTANT)
                "ledger_count": metrics["ledger_count"],
            },
            "claims": {
                "used": claim_count,
                "limit": limits["claim_limit"],
                "ratio": ratio(claim_count, limits["claim_limit"]),
                "status": status(claim_count, limits["claim_limit"]),
            },
            "storage_mb": {
                "used": storage_used_mb,
                "limit": limits["storage_limit_mb"],
                "ratio": ratio(storage_used_mb, limits["storage_limit_mb"]),
                "status": status(storage_used_mb, limits["storage_limit_mb"]),
            },
        }

        upgrade = build_upgrade_recommendation(
            governance_state["configured_plan_code"],
            governance_state["effective_plan_code"],
            usage,
            plan_mismatch=governance_state["plan_mismatch"],
        )

        # ✅ MOVE THESE INSIDE TRY
        effective_plan_definition = resolve_effective_plan_definition(workspace)
        configured_plan_definition = get_plan_definition(workspace.plan_code)

        return {
            "workspace_id": workspace.id,
            "plan_code": normalize_plan_code(workspace.plan_code),
            "billing_status": normalize_billing_status(workspace.billing_status),
            "effective_plan_code": governance_state["effective_plan_code"],

            "usage": usage,
            "metrics": metrics,
            "upgrade_recommendation": upgrade,

            # ✅ REQUIRED FOR UI
            "plan_catalog": get_plan_catalog(),

            "configured_plan_detail": {
                "code": configured_plan_definition["code"],
                "name": configured_plan_definition["name"],
                "description": configured_plan_definition["description"],
                "recommended_for": configured_plan_definition["recommended_for"],
                "billing": configured_plan_definition["billing"],
            },
            "effective_plan_detail": {
                "code": effective_plan_definition["code"],
                "name": effective_plan_definition["name"],
                "description": effective_plan_definition["description"],
                "recommended_for": effective_plan_definition["recommended_for"],
                "billing": effective_plan_definition["billing"],
            },
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"USAGE_ENDPOINT_ERROR: {str(e)}"
        )


    return {
        "workspace_id": workspace.id,
        "plan_code": normalize_plan_code(workspace.plan_code),
        "billing_status": normalize_billing_status(workspace.billing_status),
        "effective_plan_code": governance_state["effective_plan_code"],
        "usage": usage,
        "metrics": metrics,
        "stripe_ready": {
            "has_customer_id": bool(workspace.stripe_customer_id),
            "has_subscription_id": bool(workspace.stripe_subscription_id),
            "integration_status": "fallback_only",
        },
        "governance": {
            "has_any_over_limit": any(row["status"] == "over_limit" for row in usage.values()),
            "has_any_at_limit": any(row["status"] == "at_limit" for row in usage.values()),
            "has_any_near_limit": any(row["status"] == "near_limit" for row in usage.values()),
            "upgrade_required_now": upgrade["upgrade_required_now"],
            "upgrade_recommended_soon": upgrade["upgrade_recommended_soon"],
            "billing_activation_recommended": upgrade["billing_activation_recommended"],
            "configured_plan_code": governance_state["configured_plan_code"],
            "effective_plan_code": governance_state["effective_plan_code"],
            "paid_access_active": governance_state["paid_access_active"],
            "plan_mismatch": governance_state["plan_mismatch"],
            "plan_mismatch_reason": governance_state["reason"],
            "plan_mismatch_message": governance_state["message"],
        },
        "upgrade_recommendation": upgrade,
        "plan_catalog": get_plan_catalog(),
        "configured_plan_detail": {
            "code": configured_plan_definition["code"],
            "name": configured_plan_definition["name"],
            "description": configured_plan_definition["description"],
            "recommended_for": configured_plan_definition["recommended_for"],
            "billing": configured_plan_definition["billing"],
        },
        "effective_plan_detail": {
            "code": effective_plan_definition["code"],
            "name": effective_plan_definition["name"],
            "description": effective_plan_definition["description"],
            "recommended_for": effective_plan_definition["recommended_for"],
            "billing": effective_plan_definition["billing"],
        },
    }


@router.get("/workspaces/{workspace_id}/members")
def list_workspace_members(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_member(workspace_id, current_user, db)

    rows = (
        db.query(WorkspaceMembership, User)
        .join(User, User.id == WorkspaceMembership.user_id)
        .filter(WorkspaceMembership.workspace_id == workspace_id)
        .order_by(WorkspaceMembership.id.asc())
        .all()
    )

    return [serialize_workspace_member(membership, user) for membership, user in rows]


@router.patch("/workspaces/{workspace_id}/members/{user_id}")
def update_workspace_member_role(
    workspace_id: int,
    user_id: int,
    payload: UpdateWorkspaceMemberRolePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_owner(workspace_id, current_user, db)

    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Workspace membership not found")

    target_role = normalize_workspace_role(payload.role)

    if membership.user_id == current_user.id and target_role != "owner":
        raise HTTPException(status_code=400, detail="Owner cannot demote themselves")

    if membership.role == "owner" and target_role != "owner":
        owner_count = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.role == "owner",
            )
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(status_code=400, detail="Workspace must retain at least one owner")

    old_role = membership.role
    membership.role = target_role
    db.commit()
    db.refresh(membership)

    log_audit_event(
        db,
        event_type="workspace_membership_role_updated",
        entity_type="workspace_membership",
        entity_id=membership.id,
        workspace_id=workspace_id,
        old_state={"role": old_role},
        new_state={"role": membership.role},
        metadata={
            "source": "workspaces.update_workspace_member_role",
            "actor_user_id": current_user.id,
            "target_user_id": user_id,
        },
    )

    user = db.query(User).filter(User.id == membership.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return serialize_workspace_member(membership, user)


@router.delete("/workspaces/{workspace_id}/members/{user_id}")
def remove_workspace_member(
    workspace_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_owner(workspace_id, current_user, db)

    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Workspace membership not found")

    if membership.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Owner cannot remove themselves from the workspace")

    if membership.role == "owner":
        owner_count = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.role == "owner",
            )
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(status_code=400, detail="Workspace must retain at least one owner")

    user = db.query(User).filter(User.id == membership.user_id).first()
    old_state = {
        "workspace_id": membership.workspace_id,
        "user_id": membership.user_id,
        "role": membership.role,
    }

    membership_id = membership.id
    db.delete(membership)
    db.commit()

    log_audit_event(
        db,
        event_type="workspace_member_removed",
        entity_type="workspace_membership",
        entity_id=membership_id,
        workspace_id=workspace_id,
        old_state=old_state,
        new_state=None,
        metadata={
            "source": "workspaces.remove_workspace_member",
            "actor_user_id": current_user.id,
            "target_user_id": user_id,
            "target_email": user.email if user else None,
        },
    )

    return {
        "removed": True,
        "workspace_id": workspace_id,
        "user_id": user_id,
    }

