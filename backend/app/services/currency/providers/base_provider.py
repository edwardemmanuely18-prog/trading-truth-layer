from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from datetime import date

from app.services.currency.currency_models import (
    ExchangeRate,
)


# ============================================================
# BASE CURRENCY PROVIDER
# ============================================================

class BaseCurrencyProvider(ABC):
    """
    Institutional currency provider contract.

    Every currency provider inside TTL must
    implement this interface.

    Examples:

    - ECB
    - ExchangeRate API
    - Open Exchange Rates
    - Institutional FX feeds
    - Future allocator providers
    """

    @property
    @abstractmethod
    def provider_name(
        self,
    ) -> str:
        """
        Human readable provider name.
        """
        pass

    @abstractmethod
    def get_live_exchange_rate(
        self,
        *,
        from_currency: str,
        to_currency: str,
    ) -> ExchangeRate:
        """
        Returns the current exchange rate.
        """
        pass

    @abstractmethod
    def get_historical_exchange_rate(
        self,
        *,
        from_currency: str,
        to_currency: str,
        lookup_date: date,
    ) -> ExchangeRate:
        """
        Returns the historical exchange rate
        used for institutional reporting.
        """
        pass

    @abstractmethod
    def supports_currency_pair(
        self,
        *,
        from_currency: str,
        to_currency: str,
    ) -> bool:
        """
        Indicates whether the provider
        supports the requested currency pair.
        """
        pass