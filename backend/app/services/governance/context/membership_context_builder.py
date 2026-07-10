from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.governance.governance_roles import (
    GovernanceRole,
)

from app.services.governance.permission_resolution_service import (
    resolve_permission_matrix,
)

from .membership_context import (
    MembershipContext,
)

from .membership_queries import (
    get_membership,
    get_user,
    get_workspace,
    get_workspace_members,
    get_workspace_invites,
)


def build_membership_context(
    db: Session,
    workspace_id: int,
    user_id: int,
) -> MembershipContext:

    membership = get_membership(
        db,
        workspace_id,
        user_id,
    )

    if membership is None:
        raise ValueError(
            "Workspace membership not found."
        )

    role = GovernanceRole.normalize(
        membership.role,
    )

    members = get_workspace_members(
        db,
        workspace_id,
    )

    invites = get_workspace_invites(
        db,
        workspace_id,
    )

    return MembershipContext(

        workspace=get_workspace(
            db,
            workspace_id,
        ),

        user=get_user(
            db,
            user_id,
        ),

        membership=membership,

        permissions=resolve_permission_matrix(
            role.value,
        ),

        pending_invites=sum(
            1
            for invite in invites
            if invite.status == "pending"
        ),

        total_members=len(members),

        total_owners=sum(
            1
            for member in members
            if GovernanceRole.normalize(
                member.role
            )
            == GovernanceRole.OWNER
        ),

        total_operators=sum(
            1
            for member in members
            if GovernanceRole.normalize(
                member.role
            )
            == GovernanceRole.OPERATOR
        ),

        total_auditors=sum(
            1
            for member in members
            if GovernanceRole.normalize(
                member.role
            )
            == GovernanceRole.AUDITOR
        ),

        invitation_history=invites,
    )