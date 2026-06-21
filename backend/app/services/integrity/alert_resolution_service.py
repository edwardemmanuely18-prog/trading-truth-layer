from datetime import datetime

from app.models.integrity_alert import (
    IntegrityAlert,
)

from app.services.integrity.alert_status import (
    STATUS_ACKNOWLEDGED,
    STATUS_INVESTIGATING,
    STATUS_RESOLVED,
    STATUS_CLOSED,
)


def acknowledge_alert(
    alert,
    user_id,
):
    alert.status = (
        STATUS_ACKNOWLEDGED
    )

    alert.acknowledged_by = (
        str(user_id)
    )

    alert.acknowledged_at = (
        datetime.utcnow()
    )


def start_investigation(
    alert,
    user_id,
    notes,
):
    alert.status = (
        STATUS_INVESTIGATING
    )

    alert.investigation_notes = (
        notes
    )

    alert.acknowledged_by = (
        str(user_id)
    )


def resolve_alert(
    alert,
    user_id,
    notes,
):
    alert.status = (
        STATUS_RESOLVED
    )

    alert.resolution_notes = (
        notes
    )

    alert.resolved_by = (
        str(user_id)
    )

    alert.resolved_at = (
        datetime.utcnow()
    )


def close_alert(
    alert,
):
    alert.status = (
        STATUS_CLOSED
    )