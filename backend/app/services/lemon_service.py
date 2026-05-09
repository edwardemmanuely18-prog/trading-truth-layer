import json
from urllib import error, request

from app.core.config import settings


def lemon_api_base_url() -> str:
    return str(
        getattr(
            settings,
            "LEMON_API_BASE_URL",
            "https://api.lemonsqueezy.com/v1"
        )
    ).rstrip("/")


def lemon_api_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.LEMON_API_KEY}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }


def lemon_is_ready() -> bool:
    return bool(
        getattr(settings, "LEMON_BILLING_ENABLED", False)
        and getattr(settings, "LEMON_API_KEY", None)
        and getattr(settings, "LEMON_STORE_ID", None)
    )


def lemon_request(
    method: str,
    path: str,
    payload: dict | None = None,
):
    url = f"{lemon_api_base_url()}{path}"

    body = None

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = request.Request(
        url=url,
        data=body,
        method=method.upper(),
        headers=lemon_api_headers(),
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
            parsed.get("errors")
            or parsed.get("message")
            or str(exc)
        )

        return None, detail

    except Exception as exc:
        return None, str(exc)


LEMON_VARIANT_MAP = {
    "starter_monthly": "",
    "starter_annual": "",
    "pro_monthly": "",
    "pro_annual": "",
    "growth_monthly": "",
    "growth_annual": "",
    "business_monthly": "",
    "business_annual": "",
}


def get_lemon_variant_id(
    plan_code: str,
    billing_cycle: str,
) -> str | None:
    key = f"{plan_code}_{billing_cycle}"
    return LEMON_VARIANT_MAP.get(key)


def create_lemon_checkout(
    *,
    workspace,
    current_user,
    plan_code: str,
    billing_cycle: str,
    checkout_intent: str,
):
    variant_id = get_lemon_variant_id(
        plan_code,
        billing_cycle,
    )

    if not variant_id:
        return None, (
            f"No Lemon variant configured for "
            f"{plan_code} ({billing_cycle})"
        )

    payload = {
        "data": {
            "type": "checkouts",
            "attributes": {
                "checkout_data": {
                    "email": (
                        workspace.billing_email
                        or current_user.email
                    ),
                    "custom": {
                        "workspace_id": str(workspace.id),
                        "workspace_name": workspace.name,
                        "owner_user_id": str(current_user.id),
                        "target_plan_code": plan_code,
                        "billing_cycle": billing_cycle,
                        "checkout_intent": checkout_intent,
                    },
                },
                "checkout_options": {
                    "embed": False,
                    "media": False,
                    "logo": True,
                },
                "product_options": {
                    "enabled_variants": [
                        int(variant_id)
                    ],
                    "redirect_url": (
                        f"{settings.FRONTEND_BASE_URL}"
                        f"/workspace/{workspace.id}"
                        f"/settings?checkout=success"
                    ),
                },
            },
            "relationships": {
                "store": {
                    "data": {
                        "type": "stores",
                        "id": str(
                            settings.LEMON_STORE_ID
                        ),
                    }
                },
                "variant": {
                    "data": {
                        "type": "variants",
                        "id": str(variant_id),
                    }
                },
            },
        }
    }

    response, error_message = lemon_request(
        "POST",
        "/checkouts",
        payload,
    )

    if error_message:
        return None, error_message

    data = (
        (response or {})
        .get("data", {})
    )

    attributes = (
        data.get("attributes", {})
    )

    checkout_url = attributes.get("url")

    if not checkout_url:
        return None, (
            "Lemon checkout URL "
            "was not returned."
        )

    return {
        "checkout_url": checkout_url,
        "variant_id": variant_id,
        "checkout_id": data.get("id"),
    }, None        