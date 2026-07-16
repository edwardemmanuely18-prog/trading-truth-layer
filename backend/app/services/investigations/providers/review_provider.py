from __future__ import annotations

from sqlalchemy.orm import Session

from ..base_provider import (
    InvestigationProvider,
)

from app.models.review_statement import (
    ReviewStatement,
)


class ReviewProvider(
    InvestigationProvider,
):

    name = "reviews"

    version = "1.0"

    priority = 500

    def collect(
        self,
        *,
        db: Session,
        workspace_id: int,
    ):

        return (

            db.query(
                ReviewStatement
            )

            .filter(
                ReviewStatement.workspace_id
                == workspace_id
            )

            .all()

        )