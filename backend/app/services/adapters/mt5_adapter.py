from app.services.adapters.base import NormalizedTradeRow


class MT5TradeAdapter:
    """
    MetaTrader 5 adaptor stub.

    This file establishes the future ingestion contract.
    Live MT5 parsing / terminal integration will be added later.
    """

    def parse(self, content: bytes) -> list[NormalizedTradeRow]:
        raise NotImplementedError("MT5 adaptor is not implemented yet")