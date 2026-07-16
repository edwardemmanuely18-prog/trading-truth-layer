from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class WorkspaceIdentity:
    """
    Canonical identity of a user inside one workspace.

    A single user may have different identities across different
    workspaces. Authorization must always evaluate against this
    object rather than the global User model.
    """

    workspace_id: int

    user_id: int

    membership_id: int

    role: str

    status: str

    invited_by: int | None

    joined_at: datetime | None

    created_at: datetime | None

    updated_at: datetime | None