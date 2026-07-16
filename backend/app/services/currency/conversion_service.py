from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.currency_rate import CurrencyRate


class CurrencyConversionService:

    @staticmethod
    def convert(
        db: Session,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
    ) -> Decimal:

        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:

            return amount

        amount_in_eur = (
            CurrencyConversionService
            ._to_eur(
                db=db,
                amount=amount,
                currency=from_currency,
            )
        )

        return (
            CurrencyConversionService
            ._from_eur(
                db=db,
                amount=amount_in_eur,
                currency=to_currency,
            )
        )

    @staticmethod
    def _to_eur(
        db: Session,
        amount: Decimal,
        currency: str,
    ) -> Decimal:

        if currency == "EUR":

            return amount

        rate = (
            CurrencyConversionService
            ._get_rate(
                db=db,
                to_currency=currency,
            )
        )

        return amount / rate

    @staticmethod
    def _from_eur(
        db: Session,
        amount: Decimal,
        currency: str,
    ) -> Decimal:

        if currency == "EUR":

            return amount

        rate = (
            CurrencyConversionService
            ._get_rate(
                db=db,
                to_currency=currency,
            )
        )

        return amount * rate

    
    @staticmethod
    def _get_rate(
        db: Session,
        to_currency: str,
    ) -> Decimal:

        rate = (

            db.query(
                CurrencyRate,
            )

            .filter(

                CurrencyRate.from_currency
                == "EUR",

                CurrencyRate.to_currency
                == to_currency,

            )

            .order_by(
                CurrencyRate.rate_date.desc(),
            )

            .first()

        )

        if rate is None:

            raise ValueError(

                f"No exchange rate found for "
                f"{to_currency}."

            )

        return Decimal(

            str(
                rate.exchange_rate
            )

        )