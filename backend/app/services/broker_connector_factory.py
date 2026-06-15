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

    if provider in [
        "mt4",
        "mt5",
        "metatrader 4",
        "metatrader 5",
    ]:
        return MT5Connector(credential)
        

    if provider in [
        "interactive_brokers",
        "interactive brokers",
        "ibkr",
    ]:
        return IBKRConnector(credential)

    raise ValueError(
        f"Unsupported broker provider: {provider}"
    )