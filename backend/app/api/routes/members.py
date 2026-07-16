from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.workspace_membership import WorkspaceMembership
from app.models.workspace import Workspace
from app.api.deps import get_current_user
from app.models.user import User

from app.models.workspace_invite import WorkspaceInvite
from app.schemas.member import (
    AcceptInviteResponse,
    AddWorkspaceMemberRequest,
)
from app.services.member_service import accept_workspace_invite

from app.services.entitlements import enforce_member_invite_allowed

from app.api.authorization_deps import (
    require_page,
)

from app.services.authorization.registry.capability_catalog import (
    MEMBER_INVITE,
)

from app.services.authorization.engine.authorization_service import (
    AuthorizationService,
)


router = APIRouter()


@router.post("/workspaces/{workspace_id}/members")
def add_member(
    workspace_id: int,
    payload: AddWorkspaceMemberRequest,
    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user),

    _context = Depends(
        require_page(
            "members",
        )
    ),
):
    # ✅ enforce plan + billing + limits
    enforce_member_invite_allowed(workspace_id, db)

    AuthorizationService.require_capability(
        _context,
        MEMBER_INVITE,
    )

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id,
        )
        .first()
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found.",
        )

    allowed_roles = {
        "member",
        "operator",
        "auditor",
    }

    if payload.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Invalid workspace role.",
        )

    existing = (
        db.query(
            WorkspaceMembership
        )
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == payload.user_id,
        )
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="User is already a workspace member.",
        )

    membership = WorkspaceMembership(
        workspace_id=workspace_id,
        user_id=payload.user_id,
        role=payload.role
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return {"message": "Member added"}


@router.post(
    "/invites/{token}/accept",
    response_model=AcceptInviteResponse,
)
def accept_invite(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return accept_workspace_invite(
        db=db,
        token=token,
        current_user=current_user,
    )