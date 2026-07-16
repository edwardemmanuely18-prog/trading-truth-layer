from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.workspace_membership import (
    WorkspaceMembership,
)

from ..base_provider import (
    InvestigationProvider,
)


class MemberProvider(
    InvestigationProvider,
):

    name = "members"

    priority = 40

    def collect(
        self,
        *,
        db: Session,
        workspace_id: int,
    ):

        return (

            db.query(
                WorkspaceMembership
            )

            .filter(
                WorkspaceMembership.workspace_id
                == workspace_id
            )

            .all()

        )