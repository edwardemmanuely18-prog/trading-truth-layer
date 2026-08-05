"""
Trading Truth Layer (TTL)

Gateway Engine

IBKR Open Orders Test
"""

from __future__ import annotations

import os

from app.services.evidence_acquisition.gateway_engine.adapters.ibkr_gateway_adapter import (
    IBKRGatewayAdapter,
)


def test_ibkr_open_orders():

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

    adapter.session.order_event.clear()

    adapter.session.reqOpenOrders()

    assert adapter.session.order_event.wait(timeout=10)

    print()

    print("Open Orders")

    if not adapter.session.orders:

        print("No open orders.")

    for order in adapter.session.orders:

        print(order)

    adapter.disconnect()

    adapter.close()