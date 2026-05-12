from sqlalchemy import Column, Integer, ForeignKey
from app.core.db import Base


class TradeTagMap(Base):
    __tablename__ = "trade_tag_map"

    id = Column(Integer, primary_key=True, index=True)

    trade_id = Column(
        Integer,
        ForeignKey("trades.id"),
        nullable=False,
        index=True,
    )

    tag_id = Column(
        Integer,
        ForeignKey("trade_tags.id"),
        nullable=False,
        index=True,
    )