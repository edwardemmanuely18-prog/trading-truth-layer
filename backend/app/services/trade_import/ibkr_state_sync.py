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
    credential,
):

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

        state = client.get_account_summary()

        if not state:

            return {
                "success": False,
                "error":
                    "Unable to load account state",
            }

        snapshot = AccountSnapshot(
            workspace_id=connection.workspace_id,
            broker_connection_id=connection.id,

            balance=float(
                state.get(
                    "CashBalance",
                    0,
                )
            ),

            equity=float(
                state.get(
                    "NetLiquidation",
                    0,
                )
            ),

            margin=None,

            free_margin=float(
                state.get(
                    "AvailableFunds",
                    0,
                )
            ),

            leverage=None,

            currency="USD",
        )

        db.add(snapshot)

        connection.account_balance = float(
            state.get(
                "CashBalance",
                0,
            )
        )

        connection.account_equity = float(
            state.get(
                "NetLiquidation",
                0,
            )
        )

        connection.broker_currency = "USD"

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
    credential,
):

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

        positions = client.get_positions()

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

            quantity = float(
                position["quantity"]
            )

            row = OpenPosition(

                workspace_id=
                    connection.workspace_id,

                broker_connection_id=
                    connection.id,

                position_id=
                    (
                        f"{position['account']}"
                        f"-"
                        f"{position['symbol']}"
                    ),

                symbol=
                    position["symbol"],

                side=
                    (
                        "buy"
                        if quantity >= 0
                        else "sell"
                    ),

                volume=
                    abs(quantity),

                open_price=
                    float(
                        position["avg_cost"]
                    ),

                current_price=0,

                floating_pnl=0,

                opened_at=None,
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