from __future__ import annotations

from copy import deepcopy

from sqlalchemy.orm import Session

from app.services.currency.conversion_service import (
    CurrencyConversionService,
)


MONETARY_FIELDS = {

    "net_profit",

    "net_pnl",

    "gross_profit",

    "gross_loss",

    "average_win",

    "average_loss",

    "expectancy",

    "max_drawdown",

}


class MetricNormalizationService:
    """
    Canonical currency normalization layer.

    Responsible for converting all monetary
    performance metrics into the canonical
    workspace reporting currency.

    This service performs NO analytics
    calculations.

    It only normalizes already-computed
    analytics payloads.
    """

    @staticmethod
    def normalize(
        *,
        db: Session,
        analytics: dict,
        from_currency: str,
        reporting_currency: str,
    ) -> dict:

        normalized = deepcopy(
            analytics,
        )

        #
        # No conversion required.
        #

        if (

            from_currency.upper()

            ==

            reporting_currency.upper()

        ):

            return normalized

        for field in MONETARY_FIELDS:

            if field not in normalized:

                continue

            value = normalized.get(
                field,
            )

            if value is None:

                continue

            normalized[field] = float(

                CurrencyConversionService.convert(

                    db=db,

                    amount=value,

                    from_currency=from_currency,

                    to_currency=reporting_currency,

                )

            )

        #
        # Metadata.
        #

        metadata = normalized.setdefault(
            "currency_metadata",
            {},
        )

        metadata["source_currency"] = (
            from_currency.upper()
        )

        metadata["reporting_currency"] = (
            reporting_currency.upper()
        )

        metadata["normalized"] = True

        return normalized