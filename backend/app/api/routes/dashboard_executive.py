from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.services.dashboard_executive_service import (
    get_dashboard_executive_summary,
)

router = APIRouter(
    prefix="/dashboard-executive",
    tags=["dashboard"],
)


@router.get("/{workspace_id}")
def executive_dashboard(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    return get_dashboard_executive_summary(
        db,
        workspace_id,
    )