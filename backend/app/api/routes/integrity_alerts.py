from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.integrity_alert import (
    IntegrityAlert,
)

from app.services.integrity.alert_resolution_service import (
    acknowledge_alert,
    start_investigation,
    resolve_alert,
    close_alert,
)

router = APIRouter(
    prefix="/integrity-alerts",
    tags=["integrity-alerts"],
)



@router.post("/{alert_id}/acknowledge")
def acknowledge(
    alert_id: int,
    db: Session = Depends(get_db),
):
    alert = (
        db.query(
            IntegrityAlert
        )
        .filter(
            IntegrityAlert.id
            == alert_id
        )
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    acknowledge_alert(
        alert,
        "system",
    )

    db.commit()

    return {
        "status":
            alert.status
    }


@router.post("/{alert_id}/resolve")
def resolve(
    alert_id: int,
    db: Session = Depends(get_db),
):
    alert = (
        db.query(
            IntegrityAlert
        )
        .filter(
            IntegrityAlert.id
            == alert_id
        )
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    resolve_alert(
        alert,
        "system",
        "Resolved manually",
    )

    db.commit()

    return {
        "status":
            alert.status
    }


@router.post("/{alert_id}/investigate")
def investigate(
    alert_id: int,
    db: Session = Depends(get_db),
):
    alert = (
        db.query(
            IntegrityAlert
        )
        .filter(
            IntegrityAlert.id
            == alert_id
        )
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    start_investigation(
        alert,
        "system",
        "Investigation started",
    )

    db.commit()

    return {
        "status":
            alert.status
    }
