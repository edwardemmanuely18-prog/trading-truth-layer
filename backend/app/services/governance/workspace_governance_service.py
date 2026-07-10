from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.workspace_membership import (
    WorkspaceMembership,
)
from app.models.workspace_invite import WorkspaceInvite

from .identity_governance_service import (
    get_workspace_identity_profiles,
)

from .identity_models import (
    WorkspaceGovernanceSnapshot,
)

from .governance_roles import GovernanceRole


def get_workspace_governance_snapshot(
    db: Session,
    workspace_id: int,
) -> WorkspaceGovernanceSnapshot:

    members = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMember.workspace_id == workspace_id
        )
        .all()
    )

    pending_invites = (
        db.query(WorkspaceInvite)
        .filter(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.status == "pending",
        )
        .count()
    )

    profiles = get_workspace_identity_profiles(
        db,
        workspace_id,
    )

    owner_count = 0
    operator_count = 0
    auditor_count = 0
    member_count = 0

    for member in members:

        role = GovernanceRole.normalize(
            member.role
        )

        match role:

            case GovernanceRole.OWNER:
                owner_count += 1

            case GovernanceRole.OPERATOR:
                operator_count += 1

            case GovernanceRole.AUDITOR:
                auditor_count += 1

            case _:
                member_count += 1

    return WorkspaceGovernanceSnapshot(

        workspace_id=workspace_id,

        member_count=len(members),

        owner_count=owner_count,

        operator_count=operator_count,

        auditor_count=auditor_count,

        pending_invites=pending_invites,

        profiles=profiles,

    )

def evaluate_governance_health(
    snapshot: WorkspaceGovernanceSnapshot,
) -> dict:

    warnings: list[str] = []

    if snapshot.owner_count == 0:
        warnings.append("No workspace owner configured.")

    if snapshot.auditor_count == 0:
        warnings.append(
            "No independent auditor assigned."
        )

    if snapshot.pending_invites > 10:
        warnings.append(
            "High number of pending invitations."
        )

    return {
        "healthy": len(warnings) == 0,
        "warnings": warnings,
    }