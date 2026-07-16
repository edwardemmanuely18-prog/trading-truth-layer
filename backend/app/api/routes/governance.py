from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user

from app.api.authorization_deps import (
    require_workspace_context,
)

from app.models.user import User

from app.services.authorization.engine.authorization_service import (
    AuthorizationService,
)

from app.services.authorization.registry.capability_catalog import (
    GOVERNANCE_READ,
)

from app.core.db import get_db

from app.services.governance.workspace_governance_snapshot_service import (
    get_workspace_governance_snapshot,
)


router = APIRouter(
    tags=["Workspace Governance"],
)


# ==========================================================
# GOVERNANCE SNAPSHOT
# ==========================================================

@router.get(
    "/workspaces/{workspace_id}/governance",
)
def workspace_governance_snapshot(

    workspace_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

    context = Depends(
        require_workspace_context(
            "governance",
        )
    ),

):  
    AuthorizationService.require_capability(
        context.access,
        GOVERNANCE_READ,
    )

    return get_workspace_governance_snapshot(

        db=db,

        workspace_id=context.workspace.id,

    )