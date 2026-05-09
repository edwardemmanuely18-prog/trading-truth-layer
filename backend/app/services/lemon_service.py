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