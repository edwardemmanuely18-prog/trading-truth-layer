from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime
import secrets

from app.core.db import get_db
from app.models.workspace import Workspace
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership
from app.models.workspace_invite import WorkspaceInvite
from app.api.deps import get_current_user
from app.services.audit_service import log_audit_event

router = APIRouter()


class WorkspaceInviteCreate(BaseModel):
    email: EmailStr
    role: str = "member"


class WorkspaceInviteAccept(BaseModel):
    token: str


def require_workspace_operator_or_owner(workspace_id: int, current_user: User, db: Session):
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

    if membership.role not in {"owner", "operator"}:
        raise HTTPException(status_code=403, detail="Operator or owner role required for this workspace")

    return membership


def serialize_invite(invite: WorkspaceInvite):
    return {
        "id": invite.id,
        "workspace_id": invite.workspace_id,
        "email": invite.email,
        "role": invite.role,
        "token": invite.token,
        "status": invite.status,
        "invited_by_user_id": invite.invited_by_user_id,
        "accepted_by_user_id": invite.accepted_by_user_id,
        "created_at": invite.created_at.isoformat() if invite.created_at else None,
        "expires_at": invite.expires_at.isoformat() if invite.expires_at else None,
        "accepted_at": invite.accepted_at.isoformat() if invite.accepted_at else None,
    }


def accept_invite_by_token(token: str, db: Session):
    normalized_token = token.strip()

    pending_invites = (
        db.query(WorkspaceInvite)
        .filter(WorkspaceInvite.status == "pending")
        .order_by(WorkspaceInvite.id.desc())
        .all()
    )

    matched_invite = None
    for row in pending_invites:
        row_token = (row.token or "").strip()
        if row_token == normalized_token:
            matched_invite = row
            break

    if not matched_invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    if matched_invite.expires_at and matched_invite.expires_at < datetime.utcnow():
        matched_invite.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="Invite has expired")

    normalized_email = (matched_invite.email or "").strip().lower()

    user = db.query(User).filter(User.email == normalized_email).first()
    if not user:
        local_name = normalized_email.split("@")[0] if "@" in normalized_email else normalized_email
        user = User(
            email=normalized_email,
            name=local_name,
            role=matched_invite.role if matched_invite.role in {"member", "operator"} else "member",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == matched_invite.workspace_id,
            WorkspaceMembership.user_id == user.id,
        )
        .first()
    )
    if not membership:
        membership = WorkspaceMembership(
            workspace_id=matched_invite.workspace_id,
            user_id=user.id,
            role=matched_invite.role,
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)

    matched_invite.status = "accepted"
    matched_invite.accepted_by_user_id = user.id
    matched_invite.accepted_at = datetime.utcnow()

    db.commit()
    db.refresh(matched_invite)

    log_audit_event(
        db,
        event_type="workspace_invite_accepted",
        entity_type="workspace_invite",
        entity_id=matched_invite.id,
        workspace_id=matched_invite.workspace_id,
        old_state={"status": "pending"},
        new_state={
            "status": matched_invite.status,
            "accepted_by_user_id": matched_invite.accepted_by_user_id,
            "accepted_at": matched_invite.accepted_at.isoformat() if matched_invite.accepted_at else None,
        },
        metadata={
            "source": "invites.accept_workspace_invite",
            "accepted_user_id": user.id,
            "email": matched_invite.email,
        },
    )

    return {
        "message": "Invite accepted",
        "invite": serialize_invite(matched_invite),
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
        },
        "membership": {
            "workspace_id": membership.workspace_id,
            "user_id": membership.user_id,
            "role": membership.role,
        },
    }


@router.post("/workspaces/{workspace_id}/invites")
def create_workspace_invite(
    workspace_id: int,
    payload: WorkspaceInviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_operator_or_owner(workspace_id, current_user, db)

    allowed_roles = {"member", "operator"}
    role = payload.role if payload.role in allowed_roles else "member"

    normalized_email = payload.email.strip().lower()

    existing_membership = (
        db.query(WorkspaceMembership)
        .join(User, User.id == WorkspaceMembership.user_id)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            User.email == normalized_email,
        )
        .first()
    )
    if existing_membership:
        raise HTTPException(status_code=400, detail="User is already a member of this workspace")

    existing_pending = (
        db.query(WorkspaceInvite)
        .filter(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.email == normalized_email,
            WorkspaceInvite.status == "pending",
        )
        .order_by(WorkspaceInvite.id.desc())
        .first()
    )
    if existing_pending:
        return serialize_invite(existing_pending)

    invite = WorkspaceInvite(
        workspace_id=workspace_id,
        email=normalized_email,
        role=role,
        token=secrets.token_urlsafe(24),
        status="pending",
        invited_by_user_id=current_user.id,
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    log_audit_event(
        db,
        event_type="workspace_invite_created",
        entity_type="workspace_invite",
        entity_id=invite.id,
        workspace_id=workspace_id,
        old_state=None,
        new_state={
            "id": invite.id,
            "workspace_id": invite.workspace_id,
            "email": invite.email,
            "role": invite.role,
            "status": invite.status,
            "token": invite.token,
        },
        metadata={
            "source": "invites.create_workspace_invite",
            "actor_user_id": current_user.id,
        },
    )

    return serialize_invite(invite)


@router.get("/workspaces/{workspace_id}/invites")
def list_workspace_invites(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_operator_or_owner(workspace_id, current_user, db)

    invites = (
        db.query(WorkspaceInvite)
        .filter(WorkspaceInvite.workspace_id == workspace_id)
        .order_by(WorkspaceInvite.id.desc())
        .all()
    )

    return [serialize_invite(invite) for invite in invites]


@router.post("/invites/accept")
def accept_workspace_invite_via_body(
    payload: WorkspaceInviteAccept,
    db: Session = Depends(get_db),
):
    return accept_invite_by_token(payload.token, db)


@router.post("/invites/{token}/accept")
def accept_workspace_invite_legacy(
    token: str,
    db: Session = Depends(get_db),
):
    return accept_invite_by_token(token, db)