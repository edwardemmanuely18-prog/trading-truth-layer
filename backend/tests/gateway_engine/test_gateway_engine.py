import os

from app.services.evidence_acquisition.gateway_engine.engine import (
    GatewayEngine,
)

from app.services.evidence_acquisition.gateway_engine.adapters.ibkr_gateway_adapter import (
    IBKRGatewayAdapter,
)

from app.services.evidence_acquisition.gateway_engine.models import (
    GatewayEvidencePackage,
)


def test_gateway_engine():

    engine = GatewayEngine()

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

    try:

        engine.register_provider(
            adapter,
        )

        package = engine.acquire(
            adapter.provider_name,
        )

        assert isinstance(
            package,
            GatewayEvidencePackage,
        )

        print()

        print("Gateway Engine")

        print("Gateway:", package.gateway is not None)

        print("Session:", package.session is not None)

        print("Authentication:", package.authentication is not None)

        print("Endpoint:", package.endpoint is not None)

        print("Connection:", package.connection is not None)

        print("Account:", package.account is not None)

        print("Instruments:", len(package.instruments))

        print("Market Data:", len(package.market_data))

        print("Quotes:", len(package.quotes))

        print("Orders:", len(package.orders))

        print("Executions:", len(package.executions))

        print("Positions:", len(package.positions))

        print("Trades:", len(package.trades))

        #
        # Canonical singleton infrastructure evidence
        #

        assert package.gateway is not None

        assert package.account is not None

        #
        # Canonical collection evidence
        #

        assert isinstance(
            package.instruments,
            list,
        )

        assert isinstance(
            package.market_data,
            list,
        )

        assert isinstance(
            package.quotes,
            list,
        )

        assert isinstance(
            package.orders,
            list,
        )

        assert isinstance(
            package.executions,
            list,
        )

        assert isinstance(
            package.positions,
            list,
        )

        assert isinstance(
            package.trades,
            list,
        )

        #
        # Live IBKR account should expose positions.
        #

        assert len(
            package.positions,
        ) >= 1

    finally:

        adapter.close()