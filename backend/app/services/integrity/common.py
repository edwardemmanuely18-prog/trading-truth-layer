from app.models.integrity_alert import (
    IntegrityAlert,
)

SEVERITY_INFO = "INFO"
SEVERITY_WARNING = "WARNING"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_FATAL = "FATAL"


def create_alert(
    db,
    workspace_id,
    severity,
    alert_type,
    entity_type,
    entity_id,
    message,
):
    existing = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.alert_type
            == alert_type,

            IntegrityAlert.entity_type
            == entity_type,

            IntegrityAlert.entity_id
            == str(entity_id),

            IntegrityAlert.status
            == "open",
        )
        .first()
    )

    if existing:
        return

    db.add(
        IntegrityAlert(
            workspace_id=workspace_id,
            severity=severity,
            alert_type=alert_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
            message=message,
        )
    )


def resolve_alert(
    db,
    alert_type,
    entity_type,
    entity_id,
):
    alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.alert_type == alert_type,
            IntegrityAlert.entity_type == entity_type,
            IntegrityAlert.entity_id == str(entity_id),
            IntegrityAlert.status == "open",
        )
        .all()
    )

    for alert in alerts:
        alert.status = "resolved"