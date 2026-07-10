from __future__ import annotations

from dataclasses import dataclass

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import (
    WorkspaceMembership,
)
from app.models.workspace_invite import (
    WorkspaceInvite,
)

from app.services.governance.identity_models import (
    PermissionMatrix,
)


# ==========================================================
# MEMBERSHIP CONTEXT
# ==========================================================

@dataclass(slots=True)
class MembershipContext:
    """
    Canonical governance context.

    Mirrors VerificationContext used by TVS.

    This object contains every piece of data
    required to evaluate one workspace identity.
    """

    workspace: Workspace

    user: User

    membership: WorkspaceMembership

    permissions: PermissionMatrix

    pending_invites: int

    total_members: int

    total_owners: int

    total_operators: int

    total_auditors: int

    invitation_history: list[WorkspaceInvite]