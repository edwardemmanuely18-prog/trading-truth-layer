from __future__ import annotations

from app.services.currency.currency_models import (
    WorkspaceCurrencyContext,
)


# ============================================================
# DEFAULT WORKSPACE CURRENCY
# ============================================================

DEFAULT_REPORTING_CURRENCY = "USD"

DEFAULT_PROVIDER = "TTL"


# ============================================================
# WORKSPACE REPORTING CURRENCY
# ============================================================

def get_workspace_currency_context(
    workspace_id: int,
) -> WorkspaceCurrencyContext:
    """
    Canonical workspace currency entry point.

    Every TTL workspace will eventually expose
    a reporting currency independent from the
    broker's native currency.

    Examples:

    Broker Currency:
        EUR

    Reporting Currency:
        USD

    ------------------------------------------------

    IMPORTANT

    Currency conversion must NEVER alter the
    canonical broker data.

    Reporting currency exists solely for
    institutional reporting and dashboard
    purposes.
    """

    #
    # Future implementation:
    #
    # Workspace settings table.
    # Billing entitlements.
    # Multi-currency workspace support.
    #

    return WorkspaceCurrencyContext(
        workspace_id=workspace_id,
        reporting_currency=DEFAULT_REPORTING_CURRENCY,
        provider=DEFAULT_PROVIDER,
    )