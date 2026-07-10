from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.workspace_membership import (
    WorkspaceMembership,
)

from app.services.governance.context.membership_context_builder import (
    build_membership_context,
)

from app.services.governance.engine.identity_evaluation_engine import (
    evaluate_identity,
)


def get_workspace_identity_profiles(

    db: Session,

    workspace_id: int,

):

    members = (

        db.query(
            WorkspaceMembership
        )

        .filter(
            WorkspaceMembership.workspace_id
            == workspace_id
        )

        .all()

    )

    profiles = []

    for member in members:

        context = build_membership_context(

            db,

            workspace_id,

            member.user_id,

        )

        profiles.append(

            evaluate_identity(

                context

            )

        )

    return profiles