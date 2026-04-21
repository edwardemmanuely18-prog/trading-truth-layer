from typing import Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    debug_user_id: Optional[int] = Query(default=None, alias="user_id"),
    db: Session = Depends(get_db),
) -> User:
    if credentials and credentials.credentials:
        try:
            payload = decode_access_token(credentials.credentials)
            subject = payload.get("sub")
            if not subject:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token",
                )

            parsed_user_id = int(subject)
            user = db.query(User).filter(User.id == parsed_user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            return user
        except (JWTError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
            )


    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )


def get_workspace_membership(
    workspace_id: int,
    current_user: User,
    db: Session,
) -> WorkspaceMembership:
    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="User is not a member of this workspace",
        )

    return membership


def require_workspace_member(
    workspace_id: int,
    current_user: User,
    db: Session,
) -> WorkspaceMembership:
    return get_workspace_membership(workspace_id, current_user, db)


def require_workspace_operator_or_owner(
    workspace_id: int,
    current_user: User,
    db: Session,
) -> WorkspaceMembership:
    membership = get_workspace_membership(workspace_id, current_user, db)

    if membership.role not in {"owner", "operator"}:
        raise HTTPException(
            status_code=403,
            detail="Operator or owner role required for this workspace",
        )

    return membership


def require_workspace_owner(
    workspace_id: int,
    current_user: User,
    db: Session,
) -> WorkspaceMembership:
    membership = get_workspace_membership(workspace_id, current_user, db)

    if membership.role != "owner":
        raise HTTPException(
            status_code=403,
            detail="Owner role required for this workspace",
        )

    return membership


def require_workspace_auditor_operator_or_owner(
    workspace_id: int,
    current_user: User,
    db: Session,
) -> WorkspaceMembership:
    membership = get_workspace_membership(workspace_id, current_user, db)

    if membership.role not in {"owner", "operator", "auditor"}:
        raise HTTPException(
            status_code=403,
            detail="Workspace access role required",
        )

    return membership