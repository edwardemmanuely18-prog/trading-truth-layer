from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
    generate_email_verification_token,
    generate_password_reset_token,
    hash_token,
)
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership
from app.models.workspace_invite import WorkspaceInvite
from datetime import datetime

from datetime import timedelta
from app.core.config import settings
from app.services.email_service import (
    send_verification_email,
    send_password_reset_email,
    send_welcome_email,
)

from fastapi import Request
from app.services.security_audit import (
    log_security_event,
)

from app.core.rate_limit import limiter


router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterPayload(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=6, max_length=200)
    workspace_name: str = Field(
        min_length=3,
        max_length=200,
    )


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordPayload(BaseModel):
    email: EmailStr


class ResetPasswordPayload(BaseModel):
    token: str
    password: str = Field(
        min_length=6,
        max_length=200,
    )


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "email_verified": user.email_verified,
    }


def get_user_workspaces(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(WorkspaceMembership, Workspace)
        .join(Workspace, Workspace.id == WorkspaceMembership.workspace_id)
        .filter(WorkspaceMembership.user_id == user_id)
        .order_by(Workspace.id.asc())
        .all()
    )

    return [
        {
            "workspace_id": workspace.id,
            "workspace_name": workspace.name,
            "workspace_role": membership.role,
        }
        for membership, workspace in rows
    ]


@router.post("/register")
@limiter.limit("3/hour")
def register(
    payload: RegisterPayload,
    request: Request,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    raw_token, hashed_token = (
        generate_email_verification_token()
    )

    user = User(
        email=payload.email,
        name=payload.name,
        role="member",
        password_hash=hash_password(payload.password),

        email_verified=False,

        email_verification_token=hashed_token,

        email_verification_expires_at=(
            datetime.utcnow()
            + timedelta(
                minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES
            )
        ),
    )
    db.add(user)
    db.flush()

    workspace_name = payload.workspace_name.strip()

    workspace = Workspace(
        name=workspace_name
    )

    db.add(workspace)
    db.flush()

    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=user.id,
        role="owner",
    )

    db.add(membership)

    created_workspace = True

    pending_invites = (
        db.query(WorkspaceInvite)
        .filter(
            WorkspaceInvite.email == payload.email,
            WorkspaceInvite.status == "pending",
        )
        .all()
    )

    for invite in pending_invites:
        existing_membership = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == invite.workspace_id,
                WorkspaceMembership.user_id == user.id,
            )
            .first()
        )

        if not existing_membership:
            membership = WorkspaceMembership(
                workspace_id=invite.workspace_id,
                user_id=user.id,
                role=invite.role,
            )

            db.add(membership)

        invite.status = "accepted"
        invite.accepted_by_user_id = user.id
        invite.accepted_at = datetime.utcnow()

    db.commit()
    db.refresh(user)

    log_security_event(
        db=db,
        event_type="register",
        user_id=user.id,
        email=user.email,
        ip_address=request.client.host,
    )

    verification_url = (
        f"{settings.FRONTEND_BASE_URL}"
        f"/verify-email"
        f"?token={raw_token}"
    )

    send_verification_email(
        user.email,
        user.name,
        verification_url,
    )

    token = create_access_token(str(user.id))
    workspaces = get_user_workspaces(db, user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user),
        "workspaces": workspaces,
    }


@router.get("/verify-email")
def verify_email(
    token: str,
    db: Session = Depends(get_db),
):
    token_hash = hash_token(token)

    user = (
        db.query(User)
        .filter(
            User.email_verification_token == token_hash,
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification token",
        )

    if user.email_verified:
        return {
            "status": "already_verified",
        }

    if (
        user.email_verification_expires_at
        and user.email_verification_expires_at < datetime.utcnow()
    ):
        raise HTTPException(
            status_code=400,
            detail="Verification token expired",
        )

    user.email_verified = True

    log_security_event(
        db=db,
        event_type="email_verified",
        user_id=user.id,
        email=user.email,
    )

    user.email_verification_token = None
    user.email_verification_expires_at = None

    db.commit()

    send_welcome_email(
        user.email,
        user.name,
    )

    return {
        "status": "verified",
    }


@router.post("/resend-verification")
@limiter.limit("5/hour")
def resend_verification(
    payload: ForgotPasswordPayload,
    request: Request,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if not user:
        return {
            "message": "Verification email sent if account exists."
        }

    if user.email_verified:
        return {
            "message": "Email already verified."
        }

    raw_token, hashed_token = (
        generate_email_verification_token()
    )

    user.email_verification_token = hashed_token

    user.email_verification_expires_at = (
        datetime.utcnow()
        + timedelta(
            minutes=settings.EMAIL_VERIFICATION_EXPIRE_MINUTES
        )
    )

    db.commit()

    verification_url = (
        f"{settings.FRONTEND_BASE_URL}"
        f"/verify-email"
        f"?token={raw_token}"
    )

    send_verification_email(
        user.email,
        user.name,
        verification_url,
    )

    log_security_event(
        db=db,
        event_type="verification_resent",
        user_id=user.id,
        email=user.email,
    )

    return {
        "message": "Verification email sent."
    }


@router.post("/forgot-password")
@limiter.limit("3/hour")
def forgot_password(
    payload: ForgotPasswordPayload,
    request: Request,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if user:
        raw_token, hashed_token = (
            generate_password_reset_token()
        )

        user.password_reset_token = hashed_token

        user.password_reset_expires_at = (
            datetime.utcnow()
            + timedelta(
                minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
            )
        )

        db.commit()

        reset_url = (
            f"{settings.FRONTEND_BASE_URL}"
            f"/reset-password"
            f"?token={raw_token}"
        )

        send_password_reset_email(
            user.email,
            user.name,
            reset_url,
        )

        log_security_event(
            db=db,
            event_type="password_reset_requested",
            user_id=user.id,
            email=user.email,
        )

    return {
        "message": (
            "If an account exists for that email,"
            " a reset link has been sent."
        )
    }


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordPayload,
    db: Session = Depends(get_db),
):
    token_hash = hash_token(
        payload.token
    )

    user = (
        db.query(User)
        .filter(
            User.password_reset_token
            == token_hash
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset token",
        )

    if (
        user.password_reset_expires_at
        and user.password_reset_expires_at
        < datetime.utcnow()
    ):
        raise HTTPException(
            status_code=400,
            detail="Reset token expired",
        )

    user.password_hash = hash_password(
        payload.password
    )

    user.password_reset_token = None
    user.password_reset_expires_at = None

    db.commit()

    log_security_event(
        db=db,
        event_type="password_reset_completed",
        user_id=user.id,
        email=user.email,
    )

    return {
        "status": "password_reset_successful"
    }


@router.post("/login")
@limiter.limit("5/minute")
def login(
    payload: LoginPayload,
    request: Request,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.password_hash:

        log_security_event(
            db=db,
            event_type="login_failed",
            email=payload.email,
            ip_address=request.client.host,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(payload.password, user.password_hash):

        log_security_event(
            db=db,
            event_type="login_failed",
            user_id=user.id,
            email=user.email,
            ip_address=request.client.host,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address",
        )

    log_security_event(
        db=db,
        event_type="login_success",
        user_id=user.id,
        email=user.email,
        ip_address=request.client.host,
    )

    token = create_access_token(str(user.id))
    workspaces = get_user_workspaces(db, user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user),
        "workspaces": workspaces,
    }


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {
        "user": serialize_user(current_user),
        "workspaces": get_user_workspaces(db, current_user.id),
    }