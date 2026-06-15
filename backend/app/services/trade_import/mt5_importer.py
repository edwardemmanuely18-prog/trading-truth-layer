from datetime import datetime, timedelta
import logging

import MetaTrader5 as mt5

from app.models.trade import Trade
from app.services.trade_import.trade_normalizer import (
    generate_trade_hash,
)
from app.models.account_snapshot import (
    AccountSnapshot,
)

from app.models.open_position import (
    OpenPosition,
)


logger = logging.getLogger(__name__)


class MT5Importer:

    def import_trades(
        self,
        db,
        connection,
        credential,
        sync_job,
    ):

        if not mt5.initialize(
            path=r"C:\Program Files\MetaTrader 5\terminal64.exe"
        ):
            return {
                "success": False,
                "error": str(mt5.last_error()),
            }

        try:

            authorized = mt5.login(
                login=int(credential.username),
                password=credential.password_encrypted,
                server=credential.server_name,
            )

            if not authorized:
                return {
                    "success": False,
                    "error": str(mt5.last_error()),
                }

            account_info = mt5.account_info()

            if account_info:

                connection.account_balance = (
                    float(account_info.balance)
                )

                connection.account_equity = (
                    float(account_info.equity)
                )

                connection.broker_currency = (
                    account_info.currency
                )

                connection.broker_leverage = (
                    int(account_info.leverage)
                )

            to_date = datetime.utcnow()

            if connection.last_sync_at:

                from_date = (
                    connection.last_sync_at
                )

            else:

                from_date = (
                    to_date - timedelta(days=3650)
                )

            deals = mt5.history_deals_get(
                from_date,
                to_date,
            )

            if deals is None:
                return {
                    "success": False,
                    "error": str(mt5.last_error()),
                }

            detected = len(deals)
            imported = 0

            positions = {}

            for deal in deals:

                if deal.type not in (
                    mt5.DEAL_TYPE_BUY,
                    mt5.DEAL_TYPE_SELL,
                ):
                    continue

                position_id = getattr(
                    deal,
                    "position_id",
                    None,
                )

                if not position_id:
                    continue

                positions.setdefault(
                    str(position_id),
                    [],
                ).append(deal)

            for (
                position_id,
                position_deals,
            ) in positions.items():

                open_deal = None
                close_deal = None

                for deal in position_deals:

                    if getattr(
                        deal,
                        "entry",
                        None,
                    ) == 0:
                        open_deal = deal

                    elif getattr(
                        deal,
                        "entry",
                        None,
                    ) == 1:
                        close_deal = deal

                if not open_deal:
                    continue

                if (
                    open_deal.price is None
                    or open_deal.price <= 0
                ):
                    continue

                if (
                    open_deal.volume is None
                    or open_deal.volume <= 0
                ):
                    continue

                trade_hash = generate_trade_hash(
                    position_id,
                    open_deal.symbol,
                    str(open_deal.time),
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
                        open_deal.symbol,

                    side=(
                        "buy"
                        if open_deal.type
                        == mt5.DEAL_TYPE_BUY
                        else "sell"
                    ),

                    opened_at=
                        datetime.utcfromtimestamp(
                            open_deal.time
                        ),

                    closed_at=(
                        datetime.utcfromtimestamp(
                            close_deal.time
                        )
                        if close_deal
                        else None
                    ),

                    entry_price=float(
                        open_deal.price
                    ),

                    exit_price=(
                        float(close_deal.price)
                        if close_deal
                        else float(
                            open_deal.price
                        )
                    ),

                    quantity=float(
                        open_deal.volume
                    ),

                    net_pnl=(
                        float(
                            close_deal.profit
                        )
                        if close_deal
                        else 0.0
                    ),

                    currency=(
                        connection.broker_currency
                        or "USD"
                    ),

                    strategy_tag=
                        "unclassified",

                    source_system="mt5",

                    broker_connection_id=
                        connection.id,

                    broker_trade_id=
                        str(open_deal.ticket),

                    broker_position_id=
                        str(position_id),

                    broker_account_id=
                        str(
                            connection.account_id
                        ),

                    broker_server=
                        connection.broker_server,

                    import_source=
                        "mt5_sync",

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

            sync_job.status = "completed"

            connection.sync_status = (
                "completed"
            )

            connection.last_sync_at = (
                datetime.utcnow()
            )

            try:

                db.commit()

            except Exception as exc:

                db.rollback()

                sync_job.status = "failed"

                connection.sync_status = (
                    "failed"
                )

                db.commit()

                return {
                    "success": False,
                    "error": str(exc),
                }

            logger.info(
                "MT5 import completed",
                extra={
                    "detected": detected,
                    "imported": imported,
                    "workspace_id": connection.workspace_id,
                    "connection_id": connection.id,
                },
            )

            return {
                "success": True,
                "records_detected": detected,
                "records_imported": imported,
                "records_skipped": (
                    detected - imported
                ),
            }

        except Exception as exc:

            logger.exception(
                "MT5 import failed"
            )

            db.rollback()

            sync_job.status = "failed"

            sync_job.error_message = (
                str(exc)
            )

            db.commit()

            return {
                "success": False,
                "error": str(exc),
            }

        finally:

            mt5.shutdown()

    def sync_account_state(
        self,
        db,
        connection,
        credential,
        sync_job,
    ):

        if not mt5.initialize(
            path=r"C:\Program Files\MetaTrader 5\terminal64.exe"
        ):
            raise Exception(
                str(mt5.last_error())
            )

        try:

            authorized = mt5.login(
                login=int(
                    credential.username
                ),
                password=
                    credential.password_encrypted,
                server=
                    credential.server_name,
            )

            if not authorized:
                raise Exception(
                    str(mt5.last_error())
                )

            account = mt5.account_info()

            if not account:
                raise Exception(
                    "Unable to load account"
                )

            snapshot = AccountSnapshot(
                workspace_id=
                    connection.workspace_id,

                broker_connection_id=
                    connection.id,

                balance=float(
                    account.balance
                ),

                equity=float(
                    account.equity
                ),

                margin=float(
                    account.margin
                ),

                free_margin=float(
                    account.margin_free
                ),

                leverage=int(
                    account.leverage
                ),

                currency=
                    account.currency,
            )

            db.add(snapshot)

            db.commit()

            return {
                "success": True,
                "records_imported": 1,
                "records_skipped": 0,
            }

        finally:

            mt5.shutdown()


    def sync_positions(
        self,
        db,
        connection,
        credential,
    ):

        if not mt5.initialize(
            path=r"C:\Program Files\MetaTrader 5\terminal64.exe"
        ):
            raise Exception(
                str(mt5.last_error())
            )

        try:

            authorized = mt5.login(
                login=int(
                    credential.username
                ),
                password=
                    credential.password_encrypted,
                server=
                    credential.server_name,
            )

            if not authorized:
                raise Exception(
                    str(mt5.last_error())
                )

            positions = mt5.positions_get()

            if positions is None:
                positions = []

            (
                db.query(OpenPosition)
                .filter(
                    OpenPosition.broker_connection_id
                    == connection.id
                )
                .delete()
            )

            imported = 0

            for position in positions:

                side = "buy"

                if (
                    position.type
                    == mt5.POSITION_TYPE_SELL
                ):
                    side = "sell"

                record = OpenPosition(
                    workspace_id=
                        connection.workspace_id,

                    broker_connection_id=
                        connection.id,

                    position_id=
                        str(position.ticket),

                    symbol=
                        position.symbol,

                    side=
                        side,

                    volume=
                        float(position.volume),

                    open_price=
                        float(position.price_open),

                    current_price=
                        float(position.price_current),

                    floating_pnl=
                        float(position.profit),

                    opened_at=
                        datetime.utcfromtimestamp(
                            position.time
                        ),
                )

                db.add(record)

                imported += 1

            db.commit()

            return {
                "success": True,
                "records_imported": imported,
            }

        finally:

            mt5.shutdown()