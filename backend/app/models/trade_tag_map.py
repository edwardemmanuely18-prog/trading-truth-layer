from sqlalchemy import Column, Integer, ForeignKey
from app.core.db import Base


class TradeTagMap(Base):
    __tablename__ = "trade_tag_map"

    id = Column(Integer, primary_key=True)
    trade_id = Column(Integer, ForeignKey("trades.id", ondelete="CASCADE"))
    tag_id = Column(Integer, ForeignKey("trade_tags.id", ondelete="CASCADE"))