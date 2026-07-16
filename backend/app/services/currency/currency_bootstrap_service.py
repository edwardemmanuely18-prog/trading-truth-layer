from datetime import date

from sqlalchemy.orm import Session

from app.models.currency_rate import CurrencyRate


class CurrencyBootstrapService:

    @staticmethod
    def has_exchange_rates(
        db: Session,
    ) -> bool:

        return (

            db.query(
                CurrencyRate,
            )
            .first()

            is not None

        )


    @staticmethod
    def has_todays_rates(
        db: Session,
    ) -> bool:

        today = date.today()

        return (

            db.query(
                CurrencyRate,
            )
            .filter(
                CurrencyRate.rate_date == today,
            )
            .first()

            is not None

        )


    @staticmethod
    def requires_synchronization(
        db: Session,
    ) -> bool:

        if not (

            CurrencyBootstrapService
            .has_exchange_rates(
                db,
            )

        ):

            return True

        if not (

            CurrencyBootstrapService
            .has_todays_rates(
                db,
            )

        ):

            return True

        return False