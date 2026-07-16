from __future__ import annotations

from sqlalchemy.orm import Session

from ..base_provider import (
    InvestigationProvider,
)

from app.models.sync_job import SyncJob

from app.models.broker_connection import (
    BrokerConnection,
)

from app.models.trade import Trade


class SyncJobProvider(
    InvestigationProvider,
):

    name = "sync"

    version = "1.0"

    priority = 300

    def collect(
        self,
        *,
        db: Session,
        workspace_id: int,
    ):

        sync_jobs = (

            db.query(
                SyncJob
            )

            .filter(
                SyncJob.workspace_id
                == workspace_id
            )

            .all()

        )

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

        trades = (

            db.query(
                Trade
            )

            .filter(
                Trade.workspace_id
                == workspace_id
            )

            .all()

        )

        return {

            "jobs": sync_jobs,

            "broker_connections": brokers,

            "trades": trades,

        }