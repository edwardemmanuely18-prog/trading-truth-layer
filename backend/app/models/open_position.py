from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
)

from app.core.db import Base


class OpenPosition(Base):

    __tablename__ = "open_positions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    workspace_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    broker_connection_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    position_id = Column(
        String,
        nullable=False,
        index=True,
    )

    symbol = Column(
        String,
        nullable=False,
    )

    side = Column(
        String,
        nullable=False,
    )

    volume = Column(
        Float,
        nullable=False,
    )

    open_price = Column(
        Float,
        nullable=False,
    )

    current_price = Column(
        Float,
        nullable=True,
    )

    floating_pnl = Column(
        Float,
        nullable=True,
    )

    opened_at = Column(
        DateTime,
        nullable=True,
    )