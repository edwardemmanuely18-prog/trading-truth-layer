from app.services.trade_import.mt5_importer import (
    MT5Importer,
)

from app.services.trade_import.ibkr_importer import (
    IBKRImporter,
)


def get_importer(provider: str):

    provider = provider.lower()

    if provider in [
        "mt4",
        "mt5",
    ]:
        return MT5Importer()

    if provider in [
        "interactive_brokers",
        "interactive brokers",
        "ibkr",
    ]:
        return IBKRImporter()

    raise Exception(
        f"Unsupported provider: {provider}"
    )