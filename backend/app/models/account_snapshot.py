from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
)

from sqlalchemy.sql import func

from app.core.db import Base


class AccountSnapshot(Base):

    __tablename__ = "account_snapshots"

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

    balance = Column(
        Float,
        nullable=False,
    )

    equity = Column(
        Float,
        nullable=False,
    )

    margin = Column(
        Float,
        nullable=True,
    )

    free_margin = Column(
        Float,
        nullable=True,
    )

    leverage = Column(
        Integer,
        nullable=True,
    )

    currency = Column(
        String,
        nullable=True,
    )

    snapshot_time = Column(
        DateTime,
        server_default=func.now(),
    )