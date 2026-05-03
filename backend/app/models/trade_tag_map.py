from sqlalchemy import Column, Integer, ForeignKey, Index
from app.core.db import Base


class TradeTagMap(Base):
    __tablename__ = "trade_tag_map"

    id = Column(Integer, primary_key=True)

    trade_id = Column(Integer, ForeignKey("trades.id", ondelete="CASCADE"), index=True)
    tag_id = Column(Integer, ForeignKey("trade_tags.id", ondelete="CASCADE"), index=True)


# ✅ DEFINE INDEXES AFTER CLASS
Index("idx_trade_tag_map_trade_id", TradeTagMap.trade_id)
Index("idx_trade_tag_map_tag_id", TradeTagMap.tag_id)