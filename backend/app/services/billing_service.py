from app.services.paddle_service import (
    paddle_is_ready,
)

from app.services.lemon_service import (
    lemon_is_ready,
)


def get_active_billing_provider() -> str:
    """
    Provider priority:
    1. Lemon
    2. Paddle
    """

    if lemon_is_ready():
        return "lemon"

    if paddle_is_ready():
        return "paddle"

    return "manual"


def get_billing_provider_label(
    provider: str,
) -> str:
    mapping = {
        "lemon": "Lemon Squeezy",
        "paddle": "Paddle",
        "manual": "Manual Billing",
    }

    return mapping.get(
        provider,
        "Unknown"
    )