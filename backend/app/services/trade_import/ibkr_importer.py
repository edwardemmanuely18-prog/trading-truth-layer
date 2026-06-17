from datetime import datetime

from app.models.trade import Trade

from app.services.trade_import.base_importer import (
    BaseTradeImporter,
)

from app.services.trade_import.trade_normalizer import (
    generate_trade_hash,
)

from app.services.trade_import.ibkr_flex_importer import (
    IBKRFlexImporter,
)

from app.services.broker_connectors.ibkr_flex_service import (
    download_flex_report,
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

        # ==========================================
        # FLEX HISTORICAL IMPORT
        # ==========================================

        if (
            getattr(
                credential,
                "flex_enabled",
                False,
            )
            and credential.flex_query_id
            and credential.flex_token_encrypted
        ):


            xml_text = download_flex_report(
                token=credential.flex_token_encrypted,
                query_id=credential.flex_query_id,
            )

            parser = IBKRFlexImporter()

            parsed = parser.parse(
                xml_text
            )

            trades = parsed["trades"]

            detected = len(
                trades
            )

            imported = 0

            for trade_row in trades:

                trade_hash = (
                    generate_trade_hash(
                        trade_row["trade_id"],
                        trade_row["symbol"],
                        trade_row["executed_at"],
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

                try:

                    opened_at = (
                        datetime.strptime(
                            trade_row["executed_at"],
                            "%Y%m%d;%H%M%S",
                        )
                    )

                except Exception:

                    opened_at = (
                        datetime.utcnow()
                    )

                trade = Trade(

                    workspace_id=
                        connection.workspace_id,

                    member_id=1,

                    symbol=
                        trade_row["symbol"],

                    side=
                        trade_row["side"].lower(),

                    opened_at=
                        opened_at,

                    closed_at=None,

                    entry_price=0.0,

                    exit_price=None,

                    quantity=1.0,

                    net_pnl=0.0,

                    currency=
                        trade_row.get(
                            "currency",
                            "USD",
                        ),

                    strategy_tag=
                        "unclassified",

                    source_system=
                        "ibkr_flex",

                    broker_connection_id=
                        connection.id,

                    broker_trade_id=
                        trade_row["trade_id"],

                    broker_account_id=
                        trade_row["account_id"],

                    broker_order_id=
                        trade_row.get(
                            "broker_order_type"
                        ),

                    broker_server=
                        trade_row.get(
                            "broker_exchange"
                        ),

                    import_source=
                        "ibkr_flex",

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

            sync_job.records_skipped = (
                detected - imported
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

        # ==========================================
        # GATEWAY LIVE EXECUTION FALLBACK
        # ==========================================

        client = IBKRGatewayClient(
            host=(
                credential.host
                or "127.0.0.1"
            ),
            port=int(
                credential.port
                or 4002
            ),
            client_id=int(
                credential.client_id
                or 1
            ),
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

            detected = len(
                executions
            )

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
                        execution[
                            "side"
                        ].lower(),

                    opened_at=
                        datetime.utcnow(),

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

                    source_system=
                        "ibkr",

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
                        "ibkr_gateway",

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

            sync_job.records_skipped = (
                detected - imported
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
            credential,
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
            credential,
        )