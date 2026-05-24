from app.services.paddle_service import paddle_is_ready
from app.services.lemon_service import lemon_is_ready


def get_available_billing_providers():
    providers = []

    if lemon_is_ready():
        providers.append("lemon")

    if paddle_is_ready():
        providers.append("paddle")

    return providers


def get_primary_billing_provider():
    providers = get_available_billing_providers()

    if not providers:
        return "manual"

    return providers[0]