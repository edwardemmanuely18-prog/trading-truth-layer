from app.services.billing.core.provider_registry import (
    get_primary_billing_provider,
)

from app.services.billing.providers.paddle_provider import (
    PaddleProvider,
)

from app.services.billing.providers.lemon_provider import (
    LemonProvider,
)


def resolve_checkout_provider():

    provider = get_primary_billing_provider()

    if provider == "paddle":
        return PaddleProvider

    if provider == "lemon":
        return LemonProvider

    return None