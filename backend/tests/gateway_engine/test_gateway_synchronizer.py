import os

from app.services.evidence_acquisition.gateway_engine.adapters.ibkr_gateway_adapter import (
    IBKRGatewayAdapter,
)

from app.services.evidence_acquisition.gateway_engine.normalizer import (
    GatewayNormalizationManager,
)

from app.services.evidence_acquisition.gateway_engine.translators import (
    GatewayTranslatorManager,
)

from app.services.evidence_acquisition.gateway_engine.synchronizer import (
    GatewaySynchronizer,
)

from app.services.evidence_acquisition.gateway_engine.models import (
    GatewayEvidencePackage,
)


def test_gateway_synchronizer():

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

    synchronizer = GatewaySynchronizer()

    package = synchronizer.synchronize(

        adapter=adapter,

        normalization_manager=GatewayNormalizationManager(),

        translator_manager=GatewayTranslatorManager(),

    )

    assert isinstance(
        package,
        GatewayEvidencePackage,
    )

    print()

    print("Gateway Evidence Package")

    print(
        "Gateways:",
        len(package.gateways),
    )

    print(
        "Accounts:",
        len(package.accounts),
    )

    print(
        "Positions:",
        len(package.positions),
    )

    print(
        "Orders:",
        len(package.orders),
    )

    print(
        "Executions:",
        len(package.executions),
    )

    print(
        "Market Data:",
        len(package.market_data),
    )

    print()

    assert len(package.gateways) >= 1

    assert len(package.accounts) >= 1

    assert len(package.positions) >= 1