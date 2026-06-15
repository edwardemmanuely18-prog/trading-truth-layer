from app.services.broker_connectors.mt5_connector import (
    MT5Connector,
)

from app.services.broker_connectors.ibkr_connector import (
    IBKRConnector,
)


def get_connector(
    provider: str,
    credential,
):
    provider = provider.lower()

    if provider == "mt5":
        return MT5Connector(credential)

    if provider == "interactive_brokers":
        return IBKRConnector(credential)

    raise ValueError(
        f"Unsupported broker provider: {provider}"
    )