from __future__ import annotations

from datetime import date

from app.services.currency.currency_models import (
    ExchangeRate,
)


# ============================================================
# CACHE POLICIES
# ============================================================

HISTORICAL_RATE_CACHE_DAYS = 36500

LIVE_RATE_CACHE_SECONDS = 300


# ============================================================
# HISTORICAL RATE CACHE
# ============================================================

def get_cached_historical_rate(
    *,
    from_currency: str,
    to_currency: str,
    lookup_date: date,
) -> ExchangeRate | None:
    """
    Returns a cached historical exchange rate.

    Historical rates are immutable once stored.

    Examples:

        EUR -> USD

        2026-07-15

    Historical rates should remain identical
    regardless of when the report is generated.

    Future responsibilities:

    - Database lookup
    - Currency normalization
    - Cache validation
    """

    return None


# ============================================================
# LIVE RATE CACHE
# ============================================================

def get_cached_live_rate(
    *,
    from_currency: str,
    to_currency: str,
) -> ExchangeRate | None:
    """
    Returns a cached live exchange rate.

    Live rates are intentionally short-lived
    and are intended exclusively for real-time
    analytics surfaces.
    """

    return None


# ============================================================
# STORE HISTORICAL RATE
# ============================================================

def cache_historical_rate(
    exchange_rate: ExchangeRate,
) -> None:
    """
    Stores a historical exchange rate.

    Historical rates are expected to remain
    immutable after insertion.

    Future responsibilities:

    - Database persistence
    - Duplicate detection
    - Provider provenance
    """

    return None


# ============================================================
# STORE LIVE RATE
# ============================================================

def cache_live_rate(
    exchange_rate: ExchangeRate,
) -> None:
    """
    Stores a live exchange rate.

    Live rates may be overwritten whenever the
    refresh interval expires.
    """

    return None


# ============================================================
# CACHE EXPIRATION POLICY
# ============================================================

def live_rate_cache_expired(
    *,
    last_updated_seconds: int,
) -> bool:
    """
    Determines whether a live rate has expired.
    """

    return (

        last_updated_seconds

        >=

        LIVE_RATE_CACHE_SECONDS

    )


# ============================================================
# HISTORICAL RATE POLICY
# ============================================================

def historical_rate_requires_lookup(
    exchange_rate: ExchangeRate | None,
) -> bool:
    """
    Historical exchange rates are immutable.

    If a historical rate already exists, TTL
    should never request it from a provider
    again.
    """

    return exchange_rate is None


# ============================================================
# CACHE POLICY ENTRY POINT
# ============================================================

def use_cache_first() -> bool:
    """
    TTL should always attempt to use the
    currency cache before requesting any
    external provider.

    This minimizes:

    - API calls
    - infrastructure costs
    - provider dependency
    """

    return True