from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.api.dependencies.auth import (
    get_current_user,
)

from app.models.user import User

from app.services.executive_dashboard_service import (
    build_executive_dashboard,
)

router = APIRouter(
    prefix="/executive-dashboard",
    tags=["Executive Dashboard"],
)


@router.get("/{workspace_id}")
def executive_dashboard(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return build_executive_dashboard(
        db=db,
        workspace_id=workspace_id,
    )