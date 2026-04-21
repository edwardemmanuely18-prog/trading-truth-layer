import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_workspace_owner
from app.core.db import get_db
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_invite import WorkspaceInvite
from app.models.workspace_membership import WorkspaceMembership
from app.services.audit_service import log_audit_event
from app.services.entitlements import enforce_member_invite_allowed

router = APIRouter()


class WorkspaceInviteCreate(BaseModel):
    email: EmailStr
    role: str = "member"


class WorkspaceInviteAccept(BaseModel):
    token: str


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


def get_workspace_or_404(workspace_id: int, db: Session) -> Workspace:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


def get_workspace_member_count(workspace_id: int, db: Session) -> int:
    return (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id)
        .count()
    )


def normalize_email(value: str | None) -> str:
    return str(value or "").strip().lower()


def normalize_invite_role(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    allowed_roles = {"member", "operator", "auditor"}
    return normalized if normalized in allowed_roles else "member"


def parse_bool_like(value: str | None) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def read_env_value_from_backend_dotenv(key: str) -> str | None:
    try:
        env_path = Path(__file__).resolve().parents[3] / ".env"
        if not env_path.exists():
            return None

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            env_key, env_value = line.split("=", 1)
            if env_key.strip() != key:
                continue

            return env_value.strip().strip('"').strip("'")
    except Exception:
        return None

    return None


def workspace_limits_disabled() -> bool:
    direct_env_value = os.getenv("DISABLE_WORKSPACE_LIMITS")
    if direct_env_value is not None:
        return parse_bool_like(direct_env_value)

    dotenv_value = read_env_value_from_backend_dotenv("DISABLE_WORKSPACE_LIMITS")
    return parse_bool_like(dotenv_value)


def expire_stale_pending_invites(workspace_id: int, db: Session):
    now = datetime.utcnow()

    pending_rows = (
        db.query(WorkspaceInvite)
        .filter(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.status == "pending",
            WorkspaceInvite.expires_at.isnot(None),
            WorkspaceInvite.expires_at < now,
        )
        .all()
    )

    if not pending_rows:
        return

    for row in pending_rows:
        old_status = row.status
        row.status = "expired"

        log_audit_event(
            db,
            event_type="workspace_invite_expired",
            entity_type="workspace_invite",
            entity_id=row.id,
            workspace_id=row.workspace_id,
            old_state={"status": old_status},
            new_state={"status": row.status},
            metadata={
                "source": "invites.expire_stale_pending_invites",
                "email": row.email,
            },
        )

    db.commit()


def enforce_workspace_member_limit(workspace_id: int, db: Session):
    if workspace_limits_disabled():
        return

    workspace = get_workspace_or_404(workspace_id, db)
    member_limit = int(workspace.member_limit or 0)
    current_member_count = get_workspace_member_count(workspace_id, db)

    if member_limit > 0 and current_member_count >= member_limit:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Member limit reached for workspace {workspace_id}. "
                f"Current members: {current_member_count}. "
                f"Plan limit: {member_limit}. "
                f"Upgrade workspace plan to invite additional members."
            ),
        )


def accept_invite_by_token(token: str, current_user: User, db: Session):
    normalized_token = token.strip()
    if not normalized_token:
        raise HTTPException(status_code=400, detail="Invite token is required")

    matched_invite = (
        db.query(WorkspaceInvite)
        .filter(WorkspaceInvite.token == normalized_token)
        .first()
    )

    if not matched_invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    normalized_invite_email = normalize_email(matched_invite.email)
    normalized_current_user_email = normalize_email(current_user.email)

    if normalized_invite_email != normalized_current_user_email:
        raise HTTPException(
            status_code=403,
            detail="Invite email does not match authenticated user",
        )

    if matched_invite.status == "accepted":
        membership = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == matched_invite.workspace_id,
                WorkspaceMembership.user_id == current_user.id,
            )
            .first()
        )

        return {
            "message": "Invite already accepted",
            "invite": serialize_invite(matched_invite),
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "role": current_user.role,
            },
            "membership": (
                {
                    "workspace_id": membership.workspace_id,
                    "user_id": membership.user_id,
                    "role": membership.role,
                }
                if membership
                else None
            ),
        }

    if matched_invite.status in {"revoked", "expired"}:
        raise HTTPException(status_code=400, detail=f"Invite is {matched_invite.status}")

    if matched_invite.expires_at and matched_invite.expires_at < datetime.utcnow():
        old_status = matched_invite.status
        matched_invite.status = "expired"
        db.commit()
        db.refresh(matched_invite)

        log_audit_event(
            db,
            event_type="workspace_invite_expired",
            entity_type="workspace_invite",
            entity_id=matched_invite.id,
            workspace_id=matched_invite.workspace_id,
            old_state={"status": old_status},
            new_state={"status": matched_invite.status},
            metadata={
                "source": "invites.accept_invite_by_token",
                "email": matched_invite.email,
            },
        )

        raise HTTPException(status_code=400, detail="Invite has expired")

    # 🔒 FINAL MEMBER LIMIT ENFORCEMENT (ON ACCEPT)
    enforce_workspace_member_limit(matched_invite.workspace_id, db)    

    existing_membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == matched_invite.workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        .first()
    )
    if existing_membership:
        raise HTTPException(status_code=400, detail="User is already a member of this workspace")

    enforce_workspace_member_limit(matched_invite.workspace_id, db)

    membership = WorkspaceMembership(
        workspace_id=matched_invite.workspace_id,
        user_id=current_user.id,
        role=normalize_invite_role(matched_invite.role),
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)

    old_state = {"status": matched_invite.status}
    matched_invite.status = "accepted"
    matched_invite.accepted_by_user_id = current_user.id
    matched_invite.accepted_at = datetime.utcnow()

    db.commit()
    db.refresh(matched_invite)

    log_audit_event(
        db,
        event_type="workspace_invite_accepted",
        entity_type="workspace_invite",
        entity_id=matched_invite.id,
        workspace_id=matched_invite.workspace_id,
        old_state=old_state,
        new_state={
            "status": matched_invite.status,
            "accepted_by_user_id": matched_invite.accepted_by_user_id,
            "accepted_at": matched_invite.accepted_at.isoformat() if matched_invite.accepted_at else None,
        },
        metadata={
            "source": "invites.accept_workspace_invite",
            "accepted_user_id": current_user.id,
            "email": matched_invite.email,
            "role": matched_invite.role,
        },
    )

    log_audit_event(
        db,
        event_type="workspace_membership_created_from_invite",
        entity_type="workspace_membership",
        entity_id=membership.id,
        workspace_id=membership.workspace_id,
        old_state=None,
        new_state={
            "workspace_id": membership.workspace_id,
            "user_id": membership.user_id,
            "role": membership.role,
        },
        metadata={
            "source": "invites.accept_invite_by_token",
            "invite_id": matched_invite.id,
            "user_id": current_user.id,
            "email": current_user.email,
        },
    )

    return {
        "message": "Invite accepted",
        "invite": serialize_invite(matched_invite),
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
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
    workspace = get_workspace_or_404(workspace_id, db)

    require_workspace_owner(workspace_id, current_user, db)
    expire_stale_pending_invites(workspace_id, db)
    enforce_member_invite_allowed(workspace_id, db)

    role = normalize_invite_role(payload.role)
    normalized_email = normalize_email(payload.email)

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
        if existing_pending.role != role:
            old_role = existing_pending.role
            existing_pending.role = role
            db.commit()
            db.refresh(existing_pending)

            log_audit_event(
                db,
                event_type="workspace_invite_role_updated",
                entity_type="workspace_invite",
                entity_id=existing_pending.id,
                workspace_id=workspace_id,
                old_state={"role": old_role},
                new_state={"role": existing_pending.role},
                metadata={
                    "source": "invites.create_workspace_invite",
                    "actor_user_id": current_user.id,
                    "email": existing_pending.email,
                },
            )
        return serialize_invite(existing_pending)

    now = datetime.utcnow()
    invite = WorkspaceInvite(
        workspace_id=workspace_id,
        email=normalized_email,
        role=role,
        token=secrets.token_urlsafe(24),
        status="pending",
        invited_by_user_id=current_user.id,
        created_at=now,
        expires_at=now + timedelta(days=7),
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
            "expires_at": invite.expires_at.isoformat() if invite.expires_at else None,
        },
        metadata={
            "source": "invites.create_workspace_invite",
            "actor_user_id": current_user.id,
            "workspace_plan_code": workspace.plan_code,
            "workspace_member_limit": workspace.member_limit,
            "workspace_limits_disabled": workspace_limits_disabled(),
        },
    )

    return serialize_invite(invite)


@router.get("/workspaces/{workspace_id}/invites")
def list_workspace_invites(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(workspace_id, db)
    require_workspace_owner(workspace_id, current_user, db)
    expire_stale_pending_invites(workspace_id, db)

    invites = (
        db.query(WorkspaceInvite)
        .filter(WorkspaceInvite.workspace_id == workspace_id)
        .order_by(WorkspaceInvite.id.desc())
        .all()
    )

    return [serialize_invite(invite) for invite in invites]


@router.post("/workspaces/{workspace_id}/invites/{invite_id}/revoke")
def revoke_workspace_invite(
    workspace_id: int,
    invite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_workspace_or_404(workspace_id, db)
    require_workspace_owner(workspace_id, current_user, db)

    invite = (
        db.query(WorkspaceInvite)
        .filter(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.id == invite_id,
        )
        .first()
    )
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")

    if invite.status != "pending":
        return serialize_invite(invite)

    old_state = {"status": invite.status}
    invite.status = "revoked"
    db.commit()
    db.refresh(invite)

    log_audit_event(
        db,
        event_type="workspace_invite_revoked",
        entity_type="workspace_invite",
        entity_id=invite.id,
        workspace_id=invite.workspace_id,
        old_state=old_state,
        new_state={"status": invite.status},
        metadata={
            "source": "invites.revoke_workspace_invite",
            "actor_user_id": current_user.id,
            "email": invite.email,
        },
    )

    return serialize_invite(invite)


@router.post("/invites/accept")
def accept_workspace_invite_via_body(
    payload: WorkspaceInviteAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return accept_invite_by_token(payload.token, current_user, db)


@router.post("/invites/{token}/accept")
def accept_workspace_invite_legacy(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return accept_invite_by_token(token, current_user, db)
