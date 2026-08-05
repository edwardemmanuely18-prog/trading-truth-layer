"""
Trading Truth Layer (TTL)

Gateway Engine

IBKR Acquire Test
"""

from __future__ import annotations

import os

from app.services.evidence_acquisition.gateway_engine.adapters.ibkr_gateway_adapter import (
    IBKRGatewayAdapter,
)


def test_ibkr_acquire():

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

    snapshot = adapter.acquire()

    print()

    print("Gateway Snapshot")

    print("Gateways:", len(snapshot.gateways))
    print("Accounts:", len(snapshot.accounts))
    print("Positions:", len(snapshot.positions))
    print("Orders:", len(snapshot.orders))
    print("Executions:", len(snapshot.executions))
    print("Market Data:", len(snapshot.market_data))
    print("Errors:", len(snapshot.errors))

    assert len(snapshot.gateways) > 0

    assert len(snapshot.accounts) > 0

    assert isinstance(
        snapshot.positions,
        list,
    )

    assert isinstance(
        snapshot.orders,
        list,
    )

    assert isinstance(
        snapshot.executions,
        list,
    )

    assert isinstance(
        snapshot.market_data,
        list,
    )

    adapter.disconnect()

    adapter.close()