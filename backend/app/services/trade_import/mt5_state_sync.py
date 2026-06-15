from datetime import datetime

from app.models.open_position import OpenPosition
from app.models.account_snapshot import (
    AccountSnapshot,
)

from app.services.broker_connectors.mt5_connector import (
    MT5Connector,
)


def sync_mt5_positions(
    db,
    connection,
    credential,
):

    connector = MT5Connector(
        credential
    )

    positions = (
        connector.sync_positions()
    )

    db.query(OpenPosition).filter(
        OpenPosition.workspace_id
        == connection.workspace_id,
        OpenPosition.broker_connection_id
        == connection.id,
    ).delete()

    imported = 0

    for position in positions:

        side = "buy"

        if getattr(
            position,
            "type",
            0,
        ) == 1:
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
        "records_detected": imported,
    }


def sync_mt5_account_state(
    db,
    connection,
    credential,
):

    connector = MT5Connector(
        credential
    )

    state = (
        connector.sync_account_state()
    )

    if not state:
        return {
            "success": False,
            "records_imported": 0,
        }

    snapshot = AccountSnapshot(
        workspace_id=
            connection.workspace_id,

        broker_connection_id=
            connection.id,

        balance=
            state["balance"],

        equity=
            state["equity"],

        margin=
            state["margin"],

        free_margin=
            state["free_margin"],

        leverage=
            state["leverage"],

        currency=
            state["currency"],
    )

    db.add(snapshot)

    db.commit()

    return {
        "success": True,
        "records_imported": 1,
        "records_detected": 1,
    }