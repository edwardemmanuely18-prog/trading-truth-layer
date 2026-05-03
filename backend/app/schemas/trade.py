from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TradeBase(BaseModel):
    member_id: int
    symbol: str
    side: str
    opened_at: datetime
    closed_at: Optional[datetime] = None
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float
    currency: str = "USD"
    net_pnl: Optional[float] = None
    tags: List[str] = []
    source_system: Optional[str] = None


class TradeCreate(TradeBase):
    pass


class TradeUpdate(TradeBase):
    pass