from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.api.deps import get_current_user

from app.models.user import User

from app.services.dashboard_service import (
    get_dashboard_overview,
)

router = APIRouter()


@router.get(
    "/workspaces/{workspace_id}/dashboard"
)
def workspace_dashboard(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return get_dashboard_overview(
        db,
        workspace_id,
    )