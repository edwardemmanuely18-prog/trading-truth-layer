from datetime import datetime

from app.models.trade import Trade

from app.services.trade_import.base_importer import (
    BaseTradeImporter,
)

from app.services.trade_import.trade_normalizer import (
    generate_trade_hash,
)

from app.services.broker_connectors.ibkr_gateway_client import (
    IBKRGatewayClient,
)

from app.services.trade_import.ibkr_state_sync import (
    sync_ibkr_account_state,
    sync_ibkr_positions,
)



class IBKRImporter(BaseTradeImporter):

    def import_trades(
        self,
        db,
        connection,
        credential,
        sync_job,
    ):

        client = IBKRGatewayClient(
            host="127.0.0.1",
            port=7497,
            client_id=1,
        )

        if not client.connect():

            return {
                "success": False,
                "error":
                    "Unable to connect to IBKR Gateway",
            }

        try:

            executions = (
                client.list_executions()
            )

            detected = len(executions)

            imported = 0

            for execution in executions:

                trade_hash = (
                    generate_trade_hash(
                        execution[
                            "execution_id"
                        ],
                        execution[
                            "symbol"
                        ],
                        execution[
                            "executed_at"
                        ],
                    )
                )

                existing = (
                    db.query(Trade)
                    .filter(
                        Trade.raw_trade_hash
                        == trade_hash
                    )
                    .first()
                )

                if existing:
                    continue

                trade = Trade(

                    workspace_id=
                        connection.workspace_id,

                    member_id=1,

                    symbol=
                        execution["symbol"],

                    side=
                        execution["side"].lower(),

                    opened_at=
                        datetime.fromisoformat(
                            execution[
                                "executed_at"
                            ]
                        ),

                    closed_at=None,

                    entry_price=float(
                        execution["price"]
                    ),

                    exit_price=None,

                    quantity=float(
                        execution["quantity"]
                    ),

                    net_pnl=0.0,

                    currency="USD",

                    strategy_tag=
                        "unclassified",

                    source_system="ibkr",

                    broker_connection_id=
                        connection.id,

                    broker_trade_id=
                        execution[
                            "execution_id"
                        ],

                    broker_account_id=
                        execution[
                            "account_id"
                        ],

                    import_source=
                        "ibkr_sync",

                    raw_trade_hash=
                        trade_hash,
                )

                db.add(trade)

                imported += 1

            sync_job.records_processed = (
                detected
            )

            sync_job.records_imported = (
                imported
            )

            db.commit()

            return {
                "success": True,
                "records_detected":
                    detected,
                "records_imported":
                    imported,
                "records_skipped":
                    detected - imported,
            }

        finally:

            client.disconnect()


    def sync_account_state(
        self,
        db,
        connection,
        credential,
        sync_job,
    ):
        return sync_ibkr_account_state(
            db,
            connection,
        )


    def sync_positions(
        self,
        db,
        connection,
        credential,
        sync_job,
    ):
        return sync_ibkr_positions(
            db,
            connection,
        )

        