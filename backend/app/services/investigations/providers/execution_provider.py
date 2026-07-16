from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.trade import Trade

from app.services.investigations.execution.execution_replay import (
    ExecutionReplayService,
)

from ..base_provider import (
    InvestigationProvider,
)


class ExecutionProvider(
    InvestigationProvider,
):

    name = "execution"

    priority = 30

    def collect(
        self,
        *,
        db: Session,
        workspace_id: int,
    ):

        trades = (

            db.query(Trade)

            .filter(
                Trade.workspace_id == workspace_id,
            )

            .all()

        )

        return ExecutionReplayService.build(
            trades,
        )