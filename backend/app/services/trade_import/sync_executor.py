# backend/app/services/trade_import/sync_executor.py

from datetime import datetime

from app.models.sync_job import SyncJob
from app.models.broker_connection import (
    BrokerConnection,
)
from app.models.broker_credential import (
    BrokerCredential,
)
from app.models.workspace import Workspace

from app.services.trade_import.importer_registry import (
    get_importer,
)
from app.services.trade_import.mt5_state_sync import (
    sync_mt5_positions,
    sync_mt5_account_state,
)
from app.services.trade_import.ibkr_state_sync import (
    sync_ibkr_positions,
    sync_ibkr_account_state,
)



def execute_sync_job(
    db,
    sync_job_id: int,
):

    sync_job = (
        db.query(SyncJob)
        .filter(
            SyncJob.id == sync_job_id
        )
        .first()
    )

    if not sync_job:
        raise Exception(
            "Sync job not found"
        )

    sync_job.status = "running"
    sync_job.started_at = datetime.utcnow()

    db.commit()

    connection = (
        db.query(BrokerConnection)
        .filter(
            BrokerConnection.id
            == sync_job.connection_id
        )
        .first()
    )

    credential = (
        db.query(BrokerCredential)
        .filter(
            BrokerCredential.connection_id
            == connection.id
        )
        .first()
    )

    importer = get_importer(
        connection.provider
    )

    try:

        if sync_job.sync_type in [
            "historical",
            "incremental",
        ]:

            result = importer.import_trades(
                db,
                connection,
                credential,
                sync_job,
            )

        elif sync_job.sync_type == "account_state":

            if connection.provider == "ibkr":

                result = sync_ibkr_account_state(
                    db,
                    connection,
                    credential,
                )

            else:

                result = importer.sync_account_state(
                    db,
                    connection,
                    credential,
                    sync_job,
                )

        elif sync_job.sync_type == "positions":

            if connection.provider == "ibkr":

                result = sync_ibkr_positions(
                    db,
                    connection,
                    credential,
                )

            else:

                result = importer.sync_positions(
                    db,
                    connection,
                    credential,
                    sync_job,
                )

        else:

            raise Exception(
                f"Unsupported sync type: "
                f"{sync_job.sync_type}"
            )

        sync_job.records_skipped = (
            result.get(
                "records_skipped",
                0,
            )
        )

        sync_job.records_processed = int(
            result.get(
                "records_detected",
                0,
            )
            or 0
        )

        sync_job.records_imported = int(
            result.get(
                "records_imported",
                0,
            )
            or 0
        )

        records_imported = (
            sync_job.records_imported
        )

        if records_imported > 0:

            workspace = (
                db.query(Workspace)
                .filter(
                    Workspace.id
                    == connection.workspace_id
                )
                .first()
            )

            if workspace:

                current_usage = (
                    getattr(
                        workspace,
                        "trades_consumed_count",
                        0,
                    )
                    or 0
                )

                workspace.trades_consumed_count = (
                    int(current_usage)
                    + records_imported
                )

        sync_job.status = "completed"

        sync_job.completed_at = (
            datetime.utcnow()
        )

        db.commit()

        return result

    except Exception as exc:

        sync_job.status = "failed"

        sync_job.error_message = (
            str(exc)
        )

        sync_job.completed_at = (
            datetime.utcnow()
        )

        db.commit()

        raise