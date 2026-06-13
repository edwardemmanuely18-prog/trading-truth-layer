from sqlalchemy.orm import Session

from app.models.integrity_alert import (
    IntegrityAlert,
)


def create_integrity_alert(
    db: Session,
    *,
    workspace_id: int,
    claim_id: int | None,
    alert_type: str,
    severity: str,
    summary: str,
):
    alert = IntegrityAlert(
        workspace_id=workspace_id,
        claim_id=claim_id,
        alert_type=alert_type,
        severity=severity,
        summary=summary,
    )

    db.add(alert)
    db.flush()

    return alert