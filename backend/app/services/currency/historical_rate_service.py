from __future__ import annotations

from datetime import date

from app.services.currency.currency_models import (
    ExchangeRate,
    HistoricalRateRequest,
)


# ============================================================
# HISTORICAL RATE LOOKUP
# ============================================================

def get_historical_exchange_rate(
    request: HistoricalRateRequest,
) -> ExchangeRate:
    """
    Canonical historical exchange rate entry point.

    Historical exchange rates are used for:

    - Claim Reports
    - Allocator Reports
    - Due Diligence Reports
    - Public Records
    - Workspace Reporting Metrics
    - Verification Surfaces

    Historical rates MUST NEVER modify the
    canonical broker values.

    --------------------------------------------------

    Examples

    EUR -> USD

    Trade Date:
        2026-07-15

    Canonical PnL:
        1200 EUR

    Reporting PnL:
        1405 USD

    Exchange Rate Date:
        2026-07-15

    --------------------------------------------------

    IMPORTANT

    Historical exchange rates must always
    correspond to the requested reporting date.
    """

    #
    # Future implementation:
    #
    # 1. Rate cache lookup.
    # 2. Provider fallback.
    # 3. ECB historical lookup.
    # 4. Provider validation.
    # 5. Currency pair normalization.
    #

    raise NotImplementedError(
        "Historical exchange rate lookup "
        "has not yet been implemented."
    )


# ============================================================
# RATE DATE NORMALIZATION
# ============================================================

def normalize_rate_date(
    lookup_date: date,
) -> date:
    """
    Normalizes the requested exchange rate date.

    Future responsibilities:

    - Weekend handling.
    - Market holidays.
    - Missing rate fallback.
    - Previous business day lookup.
    """

    return lookup_date


# ============================================================
# CURRENCY PAIR NORMALIZATION
# ============================================================

def normalize_currency_pair(
    from_currency: str,
    to_currency: str,
) -> tuple[str, str]:
    """
    Canonical currency pair normalization.

    Examples:

        eur -> EUR
        usd -> USD

    Currency conversion logic should never
    depend upon user supplied casing.
    """

    return (
        from_currency.upper(),
        to_currency.upper(),
    )