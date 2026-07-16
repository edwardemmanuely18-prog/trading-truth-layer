from __future__ import annotations

from sqlalchemy.orm import Session

from ..base_provider import (
    InvestigationProvider,
)

from app.models.broker_connection import (
    BrokerConnection,
)


class BrokerProvider(
    InvestigationProvider,
):

    name = "brokers"

    version = "1.0"

    priority = 600

    def collect(
        self,
        *,
        db: Session,
        workspace_id: int,
    ):

        brokers = (

            db.query(
                BrokerConnection
            )

            .filter(
                BrokerConnection.workspace_id
                == workspace_id
            )

            .all()

        )

        return {

            "connections": brokers,

            "count": len(
                brokers,
            ),

        }