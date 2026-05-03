from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.db import Base


class TradeTag(Base):
    __tablename__ = "trade_tags"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)

    from sqlalchemy import UniqueConstraint

    __table_args__ = (
        UniqueConstraint("workspace_id", "name", name="uq_workspace_tag"),
    )