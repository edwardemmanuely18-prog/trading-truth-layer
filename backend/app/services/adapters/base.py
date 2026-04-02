from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol


@dataclass
class NormalizedTradeRow:
    member_id: int
    symbol: str
    side: str
    opened_at: datetime
    entry_price: float
    quantity: float
    currency: str = "USD"
    closed_at: Optional[datetime] = None
    exit_price: Optional[float] = None
    net_pnl: Optional[float] = None
    strategy_tag: Optional[str] = None
    source_system: Optional[str] = None


class TradeSourceAdapter(Protocol):
    def parse(self, content: bytes) -> list[NormalizedTradeRow]:
        ...