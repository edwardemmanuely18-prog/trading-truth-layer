from __future__ import annotations

from dataclasses import dataclass

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership

from app.services.authorization.context.access_context import (
    AccessContext,
)


@dataclass(frozen=True)
class WorkspaceContext:

    workspace: Workspace

    membership: WorkspaceMembership

    current_user: User

    access: AccessContext