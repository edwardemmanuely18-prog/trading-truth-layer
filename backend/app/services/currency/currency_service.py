from __future__ import annotations

from datetime import date

from app.services.currency.currency_models import (
    CurrencyConversionResult,
    HistoricalRateRequest,
    LiveRateRequest,
)

from app.services.currency.historical_rate_service import (
    get_historical_exchange_rate,
)

from app.services.currency.live_rate_service import (
    get_live_exchange_rate,
)

from app.services.currency.base_currency_service import (
    get_workspace_currency_context,
)


# ============================================================
# HISTORICAL CONVERSION
# ============================================================

def convert_historical_amount(
    *,
    workspace_id: int,
    amount: float,
    canonical_currency: str,
    conversion_date: date,
) -> CurrencyConversionResult:
    """
    Canonical historical currency conversion.

    Used by:

    - Claim Reports
    - Allocator Reports
    - Due Diligence Reports
    - Public Records
    - Verification Reports
    """

    workspace_context = (

        get_workspace_currency_context(
            workspace_id,
        )

    )

    reporting_currency = (

        workspace_context.reporting_currency

    )

    #
    # No conversion required.
    #

    if (

        canonical_currency.upper()

        ==

        reporting_currency.upper()

    ):

        return CurrencyConversionResult(

            canonical_amount=amount,

            canonical_currency=canonical_currency,

            reporting_amount=amount,

            reporting_currency=reporting_currency,

            exchange_rate=1.0,

            exchange_rate_date=conversion_date,

            provider="TTL",

        )

    rate = (

        get_historical_exchange_rate(

            HistoricalRateRequest(

                from_currency=canonical_currency,

                to_currency=reporting_currency,

                lookup_date=conversion_date,

            )

        )

    )

    return CurrencyConversionResult(

        canonical_amount=amount,

        canonical_currency=canonical_currency,

        reporting_amount=round(
            amount * rate.rate,
            2,
        ),

        reporting_currency=reporting_currency,

        exchange_rate=rate.rate,

        exchange_rate_date=rate.rate_date,

        provider=rate.provider,

    )


# ============================================================
# LIVE CONVERSION
# ============================================================

def convert_live_amount(
    *,
    workspace_id: int,
    amount: float,
    canonical_currency: str,
) -> CurrencyConversionResult:
    """
    Canonical live currency conversion.

    Used by:

    - Dashboards
    - Analytics pages
    - Leaderboards
    - Workspace metrics
    """

    workspace_context = (

        get_workspace_currency_context(
            workspace_id,
        )

    )

    reporting_currency = (

        workspace_context.reporting_currency

    )

    #
    # No conversion required.
    #

    if (

        canonical_currency.upper()

        ==

        reporting_currency.upper()

    ):

        return CurrencyConversionResult(

            canonical_amount=amount,

            canonical_currency=canonical_currency,

            reporting_amount=amount,

            reporting_currency=reporting_currency,

            exchange_rate=1.0,

            exchange_rate_date=date.today(),

            provider="TTL",

        )

    rate = (

        get_live_exchange_rate(

            LiveRateRequest(

                from_currency=canonical_currency,

                to_currency=reporting_currency,

            )

        )

    )

    return CurrencyConversionResult(

        canonical_amount=amount,

        canonical_currency=canonical_currency,

        reporting_amount=round(
            amount * rate.rate,
            2,
        ),

        reporting_currency=reporting_currency,

        exchange_rate=rate.rate,

        exchange_rate_date=rate.rate_date,

        provider=rate.provider,

    )


# ============================================================
# REPORTING CURRENCY
# ============================================================

def get_reporting_currency(
    workspace_id: int,
) -> str:
    """
    Returns the canonical reporting currency
    for the workspace.
    """

    return (

        get_workspace_currency_context(
            workspace_id,
        ).reporting_currency

    )