"""
Trading Truth Layer (TTL)

Gateway Engine

IBKR Account Summary Test
"""

from __future__ import annotations

import os

from app.services.evidence_acquisition.gateway_engine.adapters.ibkr_gateway_adapter import (
    IBKRGatewayAdapter,
)


def test_ibkr_account_summary():

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
    # Clear previous snapshot
    #

    adapter.session.account_summary.clear()

    adapter.session.account_summary_event.clear()

    #
    # Request account summary
    #

    adapter.session.reqAccountSummary(

        1,

        "All",

        "NetLiquidation,"
        "BuyingPower,"
        "CashBalance,"
        "AvailableFunds,"
        "ExcessLiquidity,"
        "EquityWithLoanValue",

    )

    #
    # Wait for completion
    #

    assert adapter.session.account_summary_event.wait(
        timeout=10,
    )

    summary = adapter.session.account_summary

    assert isinstance(
        summary,
        dict,
    )

    print()

    print("Account Summary")

    for tag, value in summary.items():

        print(

            f"{tag}: {value}"

        )

    adapter.disconnect()

    adapter.close()