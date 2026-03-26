from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterPayload(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=6, max_length=200)
    workspace_name: Optional[str] = None


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
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
def register(payload: RegisterPayload, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        name=payload.name,
        role="member",
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()

    if payload.workspace_name:
        workspace = Workspace(name=payload.workspace_name)
        db.add(workspace)
        db.flush()

        membership = WorkspaceMembership(
            workspace_id=workspace.id,
            user_id=user.id,
            role="owner",
        )
        db.add(membership)

    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id))
    workspaces = get_user_workspaces(db, user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user),
        "workspaces": workspaces,
    }


@router.post("/login")
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
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