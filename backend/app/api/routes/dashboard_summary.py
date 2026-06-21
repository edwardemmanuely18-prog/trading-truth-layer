from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db

from app.services.dashboard_summary_service import (
    build_dashboard_summary
)

router = APIRouter(
    prefix="/dashboard-summary",
    tags=["dashboard-summary"],
)

@router.get("/{workspace_id}")
def get_dashboard_summary(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    return build_dashboard_summary(
        db,
        workspace_id,
    )