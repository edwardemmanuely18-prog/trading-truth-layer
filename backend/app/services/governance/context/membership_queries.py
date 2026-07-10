from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import (
    WorkspaceMembership,
)
from app.models.workspace_invite import (
    WorkspaceInvite,
)


def get_workspace(
    db: Session,
    workspace_id: int,
):

    return (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )


def get_membership(
    db: Session,
    workspace_id: int,
    user_id: int,
):

    return (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
        )
        .first()
    )


def get_user(
    db: Session,
    user_id: int,
):

    return (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )


def get_workspace_members(
    db: Session,
    workspace_id: int,
):

    return (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id
        )
        .all()
    )


def get_workspace_invites(
    db: Session,
    workspace_id: int,
):

    return (
        db.query(WorkspaceInvite)
        .filter(
            WorkspaceInvite.workspace_id == workspace_id
        )
        .all()
    )