from sqlalchemy.orm import Session

from app.services.currency.rate_sync_service import (
    CurrencyRateSyncService,
)


class CurrencySynchronizationService:

    @staticmethod
    def synchronize(
        db: Session,
    ) -> int:

        synced_rates = (
            CurrencyRateSyncService.sync(
                db=db,
            )
        )

        return synced_rates