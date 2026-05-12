from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.workspace_invite import WorkspaceInvite
from app.models.workspace_membership import WorkspaceMembership
from app.models.user import User


def accept_workspace_invite(
    db: Session,
    token: str,
    current_user: User,
):
    invite = (
        db.query(WorkspaceInvite)
        .filter(WorkspaceInvite.token == token)
        .first()
    )

    if not invite:
        raise HTTPException(
            status_code=404,
            detail="Invite not found",
        )

    # normalize emails before comparison
    invite_email = (invite.email or "").strip().lower()
    current_email = (current_user.email or "").strip().lower()

    # enforce invite ownership
    if invite_email != current_email:
        raise HTTPException(
            status_code=400,
            detail="Invite email does not match authenticated user",
        )

    if invite.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Invite is no longer active",
        )

    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Invite expired",
        )

    existing_membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == invite.workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        .first()
    )

    if existing_membership:
        raise HTTPException(
            status_code=400,
            detail="User already belongs to workspace",
        )

    membership = WorkspaceMembership(
        workspace_id=invite.workspace_id,
        user_id=current_user.id,
        role=invite.role,
    )

    db.add(membership)

    invite.status = "accepted"
    invite.accepted_by_user_id = current_user.id
    invite.accepted_at = datetime.utcnow()

    db.commit()

    return {
        "message": "Workspace invite accepted",
        "workspace_id": invite.workspace_id,
        "role": invite.role,
    }