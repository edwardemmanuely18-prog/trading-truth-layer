"""
Trading Truth Layer (TTL)

Gateway Engine

IBKR Managed Accounts Test
"""

from __future__ import annotations

import os
import time

from app.services.evidence_acquisition.gateway_engine.adapters.ibkr_gateway_adapter import (
    IBKRGatewayAdapter,
)


def test_ibkr_managed_accounts():

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
    # Request managed accounts
    #

    adapter.session.reqManagedAccts()

    #
    # Give Gateway time to respond
    #

    for second in range(10):

        time.sleep(1)

        print()

        print(f"Second {second + 1}")

        print(
            "Connected:",
            adapter.session.isConnected(),
        )

        print(
            "Managed Accounts:",
            adapter.session.managed_accounts,
        )

        print(
            "Errors:",
            adapter.session.errors,
        )

    accounts = adapter.session.managed_accounts

    assert accounts is not None

    assert isinstance(
        accounts,
        list,
    )

    assert len(accounts) > 0

    print()

    print("Managed Accounts")

    for account in accounts:

        print(account)

    adapter.disconnect()

    adapter.close()