from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.user import User

from app.services.authorization.authorization_snapshot_service import (
    get_workspace_authorization,
)

router = APIRouter(prefix="/authorization", tags=["Authorization"])


@router.get("/workspaces/{workspace_id}")
def get_authorization(

    workspace_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user),

):

    return get_workspace_authorization(

        db=db,

        workspace_id=workspace_id,

        user_id=current_user.id,

    )