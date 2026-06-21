from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.integrity_alert import (
    IntegrityAlert,
)

router = APIRouter(
    prefix="/integrity-alert-feed",
    tags=["integrity-alert-feed"],
)


@router.get("/{workspace_id}")
def get_alert_feed(
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
            "id": alert.id,
            "severity": alert.severity,
            "alert_type": alert.alert_type,
            "status": alert.status,
            "message": alert.message,
            "created_at": alert.created_at,
            "acknowledged_by":
                alert.acknowledged_by,
            "resolved_by":
                alert.resolved_by,

            "acknowledged_at":
                alert.acknowledged_at,

            "resolved_at":
                alert.resolved_at,

            "acknowledged_by":
                alert.acknowledged_by,

            "resolved_by":
                alert.resolved_by,
        }
        for alert in alerts
    ]