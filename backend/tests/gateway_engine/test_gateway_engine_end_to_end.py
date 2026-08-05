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


def test_gateway_engine_end_to_end():

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

        #
        # ------------------------------------------------------------------
        # Provider Registration
        # ------------------------------------------------------------------
        #

        engine.register_provider(
            adapter,
        )

        assert (
            adapter.provider_name
            in engine.providers
        )

        #
        # ------------------------------------------------------------------
        # Acquisition
        # ------------------------------------------------------------------
        #

        package = engine.acquire(
            adapter.provider_name,
        )

        assert isinstance(
            package,
            GatewayEvidencePackage,
        )

        #
        # ------------------------------------------------------------------
        # Canonical Evidence
        # ------------------------------------------------------------------
        #

        assert package.gateway is not None

        assert package.account is not None

        assert isinstance(
            package.positions,
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
            package.trades,
            list,
        )

        #
        # ------------------------------------------------------------------
        # Diagnostics
        # ------------------------------------------------------------------
        #

        diagnostics = adapter.diagnostics()

        assert diagnostics["health"]["connected"]

        assert diagnostics["health"]["provider_name"] == (
            adapter.provider_name
        )

        #
        # ------------------------------------------------------------------
        # Statistics
        # ------------------------------------------------------------------
        #

        statistics = adapter.statistics_summary()

        assert statistics["acquisitions"] >= 1

        #
        # ------------------------------------------------------------------
        # Output
        # ------------------------------------------------------------------
        #

        print()

        print("=" * 70)

        print("Gateway Engine End-to-End Validation")

        print("=" * 70)

        print()

        print("Provider :", adapter.provider_name)

        print("Connected:", adapter.is_connected)

        print()

        print("Gateway        :", package.gateway is not None)

        print("Account        :", package.account is not None)

        print("Orders         :", len(package.orders))

        print("Positions      :", len(package.positions))

        print("Executions     :", len(package.executions))

        print("Trades         :", len(package.trades))

        print()

        print("Diagnostics")

        print(diagnostics)

        print()

        print("Statistics")

        print(statistics)

        print()

        print("END-TO-END VALIDATION PASSED")

        print("=" * 70)

    finally:

        adapter.disconnect()

        adapter.close()

        #
        # Ensure the engine itself releases every provider.
        #

        engine.shutdown()