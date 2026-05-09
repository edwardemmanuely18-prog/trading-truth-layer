import json
from urllib import error, request

from app.core.config import settings


def paddle_api_base_url() -> str:
    return str(
        getattr(
            settings,
            "PADDLE_API_BASE_URL",
            "https://api.paddle.com"
        )
    ).rstrip("/")


def paddle_api_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.PADDLE_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def paddle_is_ready() -> bool:
    return bool(
        getattr(settings, "PADDLE_BILLING_ENABLED", False)
        and getattr(settings, "PADDLE_API_KEY", None)
    )


def paddle_request(
    method: str,
    path: str,
    payload: dict | None = None,
):
    url = f"{paddle_api_base_url()}{path}"

    body = None

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = request.Request(
        url=url,
        data=body,
        method=method.upper(),
        headers=paddle_api_headers(),
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
            or str(exc)
        )

        return None, detail

    except Exception as exc:
        return None, str(exc)


def get_paddle_environment() -> str:
    api_key = str(
        getattr(settings, "PADDLE_API_KEY", "") or ""
    ).lower()

    if api_key.startswith("test_"):
        return "sandbox"

    return "live"