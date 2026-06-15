from app.models.account_snapshot import (
    AccountSnapshot,
)

from app.models.open_position import (
    OpenPosition,
)

from app.services.broker_connectors.ibkr_gateway_client import (
    IBKRGatewayClient,
)


def sync_ibkr_account_state(
    db,
    connection,
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

        state = client.get_account_state()

        if not state:

            return {
                "success": False,
                "error":
                    "Unable to load account state",
            }

        snapshot = AccountSnapshot(

            workspace_id=
                connection.workspace_id,

            broker_connection_id=
                connection.id,

            balance=
                float(
                    state["balance"]
                ),

            equity=
                float(
                    state["equity"]
                ),

            margin=
                float(
                    state["margin"]
                ),

            free_margin=
                float(
                    state["free_margin"]
                ),

            leverage=
                int(
                    state["leverage"]
                ),

            currency=
                state["currency"],
        )

        db.add(snapshot)

        connection.account_balance = (
            float(
                state["balance"]
            )
        )

        connection.account_equity = (
            float(
                state["equity"]
            )
        )

        connection.broker_currency = (
            state["currency"]
        )

        connection.broker_leverage = (
            int(
                state["leverage"]
            )
        )

        db.commit()

        return {
            "success": True,
            "records_detected": 1,
            "records_imported": 1,
            "records_skipped": 0,
        }

    finally:

        client.disconnect()


def sync_ibkr_positions(
    db,
    connection,
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

        positions = (
            client.list_positions()
        )

        detected = len(
            positions
        )

        imported = 0

        db.query(
            OpenPosition
        ).filter(
            OpenPosition.broker_connection_id
            == connection.id
        ).delete()

        for position in positions:

            row = OpenPosition(

                workspace_id=
                    connection.workspace_id,

                broker_connection_id=
                    connection.id,

                position_id=
                    position[
                        "position_id"
                    ],

                symbol=
                    position[
                        "symbol"
                    ],

                side=
                    position[
                        "side"
                    ],

                volume=float(
                    position[
                        "quantity"
                    ]
                ),

                open_price=float(
                    position[
                        "average_price"
                    ]
                ),

                current_price=float(
                    position[
                        "market_price"
                    ]
                ),

                floating_pnl=float(
                    position[
                        "unrealized_pnl"
                    ]
                ),
            )

            db.add(row)

            imported += 1

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