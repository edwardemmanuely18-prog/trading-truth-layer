from __future__ import annotations

from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership
from app.models.user import User

from app.services.authorization.context.access_context_builder import (
    AccessContextBuilder,
)

from .workspace_context import WorkspaceContext


class WorkspaceContextBuilder:

    @staticmethod
    def build(
        db: Session,
        workspace_id: int,
        current_user: User,
    ) -> WorkspaceContext:

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

        membership = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.user_id == current_user.id,
            )
            .first()
        )

        if membership is None:

            raise HTTPException(
                status_code=403,
                detail="Not a workspace member.",
            )

        access = AccessContextBuilder.build(
            db=db,
            workspace_id=workspace_id,
            user_id=current_user.id,
        )

        return WorkspaceContext(
            workspace=workspace,
            membership=membership,
            current_user=current_user,
            access=access,
        )