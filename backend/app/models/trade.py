from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.db import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    member_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False)
    opened_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    net_pnl = Column(Float, nullable=True)
    currency = Column(String, nullable=False, default="USD")
    strategy_tag = Column(String, nullable=True)
    source_system = Column(String, nullable=True)
    trade_fingerprint = Column(String, nullable=True, index=True)