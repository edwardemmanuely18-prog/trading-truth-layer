from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
)

from sqlalchemy.sql import func

from app.core.db import Base


class BrokerConnection(Base):
    __tablename__ = "broker_connections"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    provider = Column(
        String,
        nullable=False,
        index=True,
    )

    connection_name = Column(
        String,
        nullable=False,
    )

    account_id = Column(
        String,
        nullable=True,
    )

    account_name = Column(
        String,
        nullable=True,
    )

    adapter_type = Column(
        String,
        nullable=False,
        default="broker_api",
    )

    sync_mode = Column(
        String,
        nullable=False,
        default="manual",
    )

    connection_status = Column(
        String,
        nullable=False,
        default="not_connected",
    )

    sync_status = Column(
        String,
        nullable=False,
        default="idle",
    )

    verification_status = Column(
        String,
        nullable=False,
        default="pending",
    )

    trust_tier = Column(
        String,
        nullable=False,
        default="tier_1",
    )

    account_environment = Column(
        String,
        nullable=False,
        default="unknown",
    )

    last_sync_at = Column(
        DateTime,
        nullable=True,
    )

    last_sync_error = Column(
        String,
        nullable=True,
    )

    verified_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    broker_account_id = Column(
        String,
        nullable=True,
    )

    broker_server = Column(
        String,
        nullable=True,
    )

    broker_currency = Column(
        String,
        nullable=True,
    )

    broker_leverage = Column(
        Integer,
        nullable=True,
    )

    account_balance = Column(
        Numeric(20, 4),
        nullable=True,
    )

    account_equity = Column(
        Numeric(20, 4),
        nullable=True,
    )