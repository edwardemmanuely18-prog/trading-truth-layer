from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


# ============================================================
# EXCHANGE RATE
# ============================================================

@dataclass(frozen=True)
class ExchangeRate:
    """
    Canonical exchange rate object.

    Represents a single currency pair and the
    exchange rate used for reporting purposes.
    """

    from_currency: str
    to_currency: str

    rate: float

    rate_date: date

    provider: str


# ============================================================
# CURRENCY CONVERSION RESULT
# ============================================================

@dataclass(frozen=True)
class CurrencyConversionResult:
    """
    Immutable currency conversion result.

    Both canonical and reporting values are
    preserved for institutional reporting.
    """

    canonical_amount: float
    canonical_currency: str

    reporting_amount: float
    reporting_currency: str

    exchange_rate: float

    exchange_rate_date: date

    provider: str


# ============================================================
# HISTORICAL RATE REQUEST
# ============================================================

@dataclass(frozen=True)
class HistoricalRateRequest:
    """
    Historical rate lookup request.

    Used primarily by allocator reports,
    claim reports and public records.
    """

    from_currency: str
    to_currency: str

    lookup_date: date


# ============================================================
# LIVE RATE REQUEST
# ============================================================

@dataclass(frozen=True)
class LiveRateRequest:
    """
    Live exchange rate request.

    Used by dashboard and real-time
    reporting surfaces.
    """

    from_currency: str
    to_currency: str


# ============================================================
# WORKSPACE CURRENCY CONTEXT
# ============================================================

@dataclass(frozen=True)
class WorkspaceCurrencyContext:
    """
    Canonical workspace reporting currency.

    Every TTL workspace will eventually have
    a reporting currency independent from the
    broker's native currency.
    """

    workspace_id: int

    reporting_currency: str

    provider: str