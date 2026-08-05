"""
Trading Truth Layer (TTL)

Gateway Engine

IBKR Position Discovery Test
"""

from __future__ import annotations

import os
import time

from app.services.evidence_acquisition.gateway_engine.adapters.ibkr_gateway_adapter import (
    IBKRGatewayAdapter,
)


def test_ibkr_positions():

    adapter = IBKRGatewayAdapter(

        host=os.getenv(
            "IBKR_HOST",
            "127.0.0.1",
        ),

        port=int(
            os.getenv(
                "IBKR_PORT",
                "4002",
            )
        ),

        client_id=int(
            os.getenv(
                "IBKR_CLIENT_ID",
                "1",
            )
        ),

    )

    adapter.initialize()

    adapter.connect()

    #
    # Request positions
    #

    adapter.session.reqPositions()

    #
    # Give Gateway time to respond
    #

    time.sleep(5)

    positions = adapter.session.positions

    assert positions is not None

    assert isinstance(
        positions,
        list,
    )

    print()

    print("Positions discovered:")

    if not positions:

        print(
            "No open positions in IBKR Paper account."
        )

    for position in positions:

        print(position)

    adapter.disconnect()