from __future__ import annotations

from dataclasses import asdict

from sqlalchemy.orm import Session

from app.models.workspace import Workspace

from app.services.governance.context.membership_context_builder import (
    build_membership_context,
)

from app.services.governance.identity_governance_service import (
    get_workspace_identity_profiles,
)

from app.services.governance.governance_health_builder import (
    build_governance_health,
)

from app.models.workspace_membership import (
    WorkspaceMembership,
)


# ==========================================================
# PUBLIC API
# ==========================================================

def get_workspace_governance_snapshot(
    db: Session,
    workspace_id: int,
):

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if workspace is None:
        return None

    memberships = (
        db.query(
            WorkspaceMembership
        )
        .filter(
            WorkspaceMembership.workspace_id
            == workspace_id
        )
        .all()
    )

    profiles = get_workspace_identity_profiles(
        db,
        workspace_id,
    )

    # ==========================================================
    # AUTHORITY DISTRIBUTION
    # ==========================================================

    authority_distribution = {

        "critical": 0,

        "high": 0,

        "medium": 0,

        "standard": 0,

    }

    for profile in profiles:

        authority = profile.authority.lower()

        if authority == "critical":
            authority_distribution["critical"] += 1

        elif authority == "high":
            authority_distribution["high"] += 1

        elif authority == "medium":
            authority_distribution["medium"] += 1

        else:
            authority_distribution["standard"] += 1

    context = None

    if memberships:
        context = build_membership_context(
            db,
            workspace_id,
            memberships[0].user_id,
        )

    governance = (
        build_governance_health(context)
        if context
        else None
    )

    return {

        "workspace": {

            "id": workspace.id,

            "name": workspace.name,

            "plan": workspace.plan_code,

        },

        "capacity": {

            "members": len(memberships),

            "member_limit": workspace.member_limit,

            "utilization": (
                round(
                    len(memberships)
                    / workspace.member_limit
                    * 100,
                    1,
                )
                if workspace.member_limit
                else 0
            ),

        },

        "identity_summary": {

            "owners": (
                context.total_owners
                if context
                else 0
            ),

            "operators": (
                context.total_operators
                if context
                else 0
            ),

            "auditors": (
                context.total_auditors
                if context
                else 0
            ),

            "members": (
                context.total_members
                if context
                else 0
            ),

        },

        "authority_distribution": authority_distribution,

        "profiles": [

            asdict(
                profile
            )

            for profile in profiles

        ],

        "governance_health": (

            asdict(governance)

            if governance

            else None

        ),

        "recommendations": (

            [
                asdict(item)
                for item in governance.recommendations
            ]

            if governance

            else []

        ),

        "governance_version": "1.0",

        "activity": {

            "status": "coming_soon",

        },

        "generated_by": "Identity Governance System",

        "snapshot_type": "workspace_governance",

    }