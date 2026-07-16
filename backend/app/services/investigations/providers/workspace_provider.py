from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.workspace import Workspace

from ..base_provider import (
    InvestigationProvider,
)


class WorkspaceProvider(
    InvestigationProvider,
):

    name = "workspace"

    version = "1.0"

    priority = 10

    def collect(
        self,
        *,
        db: Session,
        workspace_id: int,
    ):

        return (
            db.query(Workspace)
            .filter(
                Workspace.id == workspace_id,
            )
            .first()
        )