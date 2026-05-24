from sqlalchemy.orm import Session

from app.models.billing.billing_event import BillingEvent


def billing_event_already_processed(
    provider_event_id: str,
    db: Session,
) -> bool:
    existing = (
        db.query(BillingEvent)
        .filter(
            BillingEvent.provider_event_id
            == provider_event_id
        )
        .first()
    )

    return existing is not None