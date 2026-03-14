from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership


def get_current_user(
    user_id: int = Query(..., description="Temporary user context for role enforcement"),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_workspace_membership(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="User is not a member of this workspace")
    return membership


def require_operator_or_owner(
    workspace_id: int,
    membership: WorkspaceMembership = Depends(get_workspace_membership),
):
    if membership.role not in {"owner", "operator"}:
        raise HTTPException(
            status_code=403,
            detail="Operator or owner role required for this workspace",
        )
    return membership


def require_auditor_or_higher(
    workspace_id: int,
    membership: WorkspaceMembership = Depends(get_workspace_membership),
):
    if membership.role not in {"owner", "operator", "auditor"}:
        raise HTTPException(
            status_code=403,
            detail="Auditor, operator, or owner role required for this workspace",
        )
    return membership