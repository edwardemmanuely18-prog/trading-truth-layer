from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from ..base_provider import (
    InvestigationProvider,
)


class ClaimProvider(
    InvestigationProvider,
):

    name = "claims"

    priority = 20

    def collect(
        self,
        *,
        db: Session,
        workspace_id: int,
    ):

        return (

            db.query(ClaimSchema)

            .filter(
                ClaimSchema.workspace_id == workspace_id,
            )

            .all()

        )