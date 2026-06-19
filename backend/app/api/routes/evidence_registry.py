from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.api.deps import (
    get_current_user,
    require_workspace_member,
)

from app.models.user import User

from app.services.evidence_registry_service import (
    get_evidence_registry,
)

router = APIRouter()


@router.get(
    "/workspaces/{workspace_id}/evidence-registry"
)
def evidence_registry(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    return get_evidence_registry(
        db,
        workspace_id,
    )