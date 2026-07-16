from sqlalchemy.orm import Session

from app.services.currency.currency_synchronization_service import (
    CurrencySynchronizationService,
)


class CurrencySchedulerService:

    @staticmethod
    def run_daily_sync(
        db: Session,
    ) -> int:

        synced_rates = (
            CurrencySynchronizationService
            .synchronize(
                db=db,
            )
        )

        return synced_rates