"""
Trading Truth Layer (TTL)

Gateway Engine

IBKR Executions Test
"""

from __future__ import annotations

import os

from app.services.evidence_acquisition.gateway_engine.adapters.ibkr_gateway_adapter import (
    IBKRGatewayAdapter,
)

from ibapi.execution import ExecutionFilter


def test_ibkr_executions():

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
    # Request executions
    #

    adapter.session.executions.clear()

    adapter.session.reqExecutions(

        1,

        ExecutionFilter(),

    )

    #
    # Give IBKR time to respond
    #

    import time

    time.sleep(5)

    print()

    print("Executions")

    if not adapter.session.executions:

        print("No executions returned.")

    for execution in adapter.session.executions:

        print(execution)

    adapter.disconnect()

    adapter.close()