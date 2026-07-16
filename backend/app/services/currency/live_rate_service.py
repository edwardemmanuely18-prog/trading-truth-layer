from __future__ import annotations

from app.services.currency.currency_models import (
    ExchangeRate,
    LiveRateRequest,
)


# ============================================================
# LIVE EXCHANGE RATE LOOKUP
# ============================================================

def get_live_exchange_rate(
    request: LiveRateRequest,
) -> ExchangeRate:
    """
    Canonical live exchange rate entry point.

    Live rates are intended exclusively for
    real-time reporting surfaces.

    Examples:

    - Dashboards
    - Workspace analytics
    - Leaderboards
    - Portfolio views
    - Institutional intelligence pages

    --------------------------------------------------

    IMPORTANT

    Live exchange rates MUST NEVER be used
    by institutional reports or verification
    surfaces.

    Historical reports must consume the
    historical rate service instead.

    --------------------------------------------------

    Live exchange rates are expected to
    fluctuate over time and therefore are
    unsuitable for immutable reporting.
    """

    #
    # Future implementation:
    #
    # 1. Rate cache lookup.
    # 2. Provider lookup.
    # 3. Provider fallback.
    # 4. Currency normalization.
    #

    raise NotImplementedError(
        "Live exchange rate lookup "
        "has not yet been implemented."
    )


# ============================================================
# LIVE RATE REFRESH POLICY
# ============================================================

def get_live_rate_refresh_interval() -> int:
    """
    Returns the refresh interval in seconds.

    Future implementations may expose this
    as a workspace setting.

    Current policy:

    300 seconds = 5 minutes.

    Live currency conversion does not require
    second-by-second exchange rate updates
    for institutional analytics.
    """

    return 300


# ============================================================
# LIVE RATE ELIGIBILITY
# ============================================================

def supports_live_conversion(
    page_name: str,
) -> bool:
    """
    Determines whether a TTL surface is
    permitted to consume live exchange rates.
    """

    supported_pages = {

        "dashboard",

        "leaderboard",

        "analytics",

        "workspace_metrics",

        "portfolio",

    }

    return page_name.lower() in supported_pages