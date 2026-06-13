from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.integrity_alert import (
    IntegrityAlert,
)

router = APIRouter()


@router.get(
    "/workspaces/{workspace_id}/integrity-alerts"
)
def get_integrity_alerts(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id
            == workspace_id
        )
        .order_by(
            IntegrityAlert.id.desc()
        )
        .all()
    )

    return [
        {
            "id": a.id,
            "claim_id": a.claim_id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "status": a.status,
            "summary": a.summary,
            "created_at": a.created_at,
        }
        for a in alerts
    ]