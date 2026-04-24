from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.workspace_membership import WorkspaceMembership
from app.models.workspace import Workspace
from app.api.deps import get_current_user
from app.models.user import User

from app.services.entitlements import enforce_member_invite_allowed

router = APIRouter()


@router.post("/workspaces/{workspace_id}/members")
def add_member(
    workspace_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ✅ enforce plan + billing + limits
    enforce_member_invite_allowed(workspace_id, db)

    membership = WorkspaceMembership(
        workspace_id=workspace_id,
        user_id=user_id,
        role="member"
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return {"message": "Member added"}