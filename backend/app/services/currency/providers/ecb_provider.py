from __future__ import annotations

from datetime import date

from app.services.currency.currency_models import (
    ExchangeRate,
)

from app.services.currency.providers.base_provider import (
    BaseCurrencyProvider,
)


class ECBProvider(
    BaseCurrencyProvider,
):
    """
    European Central Bank exchange rate provider.

    The ECB publishes institutional reference
    exchange rates suitable for historical
    reporting and allocator-grade documentation.

    Currency conversion logic, caching and
    reporting decisions are intentionally
    delegated to the currency services.
    """

    @property
    def provider_name(
        self,
    ) -> str:

        return "ECB"


    def get_live_exchange_rate(
        self,
        *,
        from_currency: str,
        to_currency: str,
    ) -> ExchangeRate:
        """
        TTL V1 intentionally uses the ECB
        daily reference rate for live
        analytics surfaces.

        The actual implementation will be
        delegated to the rate cache service.
        """

        raise NotImplementedError(
            "ECB live exchange rate lookup "
            "has not yet been implemented."
        )


    def get_historical_exchange_rate(
        self,
        *,
        from_currency: str,
        to_currency: str,
        lookup_date: date,
    ) -> ExchangeRate:
        """
        Returns the ECB historical reference
        rate for the supplied date.

        The actual provider implementation
        will be wired after the CurrencyRate
        persistence layer is connected.
        """

        raise NotImplementedError(
            "ECB historical exchange rate "
            "lookup has not yet been implemented."
        )


    def supports_currency_pair(
        self,
        *,
        from_currency: str,
        to_currency: str,
    ) -> bool:
        """
        Currency pair validation is delegated
        to the supported currency registry.

        ECB can therefore support every
        fiat currency pair that TTL permits.
        """

        return True