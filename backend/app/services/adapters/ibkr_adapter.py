from app.services.adapters.base import NormalizedTradeRow


class IBKRTradeAdapter:
    """
    Interactive Brokers adapter stub.

    Future support:
    - Flex Queries
    - TWS Gateway
    - Execution synchronization
    """

    def parse(self, content: bytes) -> list[NormalizedTradeRow]:
        raise NotImplementedError(
            "IBKR adapter is not implemented yet"
        )