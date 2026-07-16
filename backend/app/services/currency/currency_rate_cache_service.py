from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.currency_rate import CurrencyRate
from app.models.workspace_preferences import (
    WorkspacePreferences,
)


class CurrencyRateCacheService:
    """
    Institutional currency rate cache.

    Loads all required exchange rates exactly once
    for a TPS normalization pass.

    No per-trade SQL queries are permitted.
    """

    @staticmethod
    def build_rate_cache(
        *,
        db: Session,
        workspace_id: int,
        currencies: set[str],
    ) -> tuple[str, dict[str, Decimal]]:

        preferences = (
            db.query(WorkspacePreferences)
            .filter(
                WorkspacePreferences.workspace_id
                == workspace_id
            )
            .first()
        )

        reporting_currency = (
            preferences.currency.upper()
            if preferences
            else "USD"
        )

        #
        # Reporting currency never requires conversion.
        #

        rate_cache = {
            reporting_currency: Decimal("1.0"),
        }

        if not currencies:

            return (
                reporting_currency,
                rate_cache,
            )

        #
        # We currently support EUR based rates.
        #

        required_currencies = {

            currency.upper()

            for currency in currencies

            if currency.upper()
            != reporting_currency

        }

        if not required_currencies:

            return (
                reporting_currency,
                rate_cache,
            )

        rates = (

            db.query(
                CurrencyRate,
            )
            .filter(
                CurrencyRate.from_currency == "EUR",
                CurrencyRate.to_currency.in_(
                    list(required_currencies),
                ),
            )
            .all()

        )

        #
        # Build cache.
        #

        eur_rates = {

            rate.to_currency.upper():
            Decimal(
                str(
                    rate.exchange_rate,
                )
            )

            for rate in rates

        }

        #
        # If reporting currency is not EUR
        # we also need its EUR rate.
        #

        if reporting_currency != "EUR":

            reporting_rate = (

                db.query(
                    CurrencyRate,
                )
                .filter(
                    CurrencyRate.from_currency == "EUR",
                    CurrencyRate.to_currency
                    == reporting_currency,
                )
                .order_by(
                    CurrencyRate.rate_date.desc(),
                )
                .first()

            )

            if reporting_rate:

                eur_rates[
                    reporting_currency
                ] = Decimal(
                    str(
                        reporting_rate.exchange_rate,
                    )
                )

        #
        # Compute conversion rates
        # relative to reporting currency.
        #

        if reporting_currency == "EUR":

            for currency, rate in eur_rates.items():

                rate_cache[currency] = rate

        else:

            reporting_rate = eur_rates.get(
                reporting_currency,
            )

            if reporting_rate:

                for currency, rate in eur_rates.items():

                    rate_cache[currency] = (

                        rate / reporting_rate

                    )

        return (
            reporting_currency,
            rate_cache,
        )