from app.models.integrity_alert import IntegrityAlert


def resolve_alert(
    db,
    alert_type,
    entity_type,
    entity_id,
):
    alert = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.alert_type == alert_type,
            IntegrityAlert.entity_type == entity_type,
            IntegrityAlert.entity_id == str(entity_id),
            IntegrityAlert.status == "open",
        )
        .first()
    )

    if alert:
        alert.status = "resolved"