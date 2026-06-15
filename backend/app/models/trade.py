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
    strategy_tag = Column(
        String,
        nullable=True,
        default="unclassified",
    )
    source_system = Column(String, nullable=True)
    trade_fingerprint = Column(String, nullable=True, index=True)

    broker_ticket = Column(
        String,
        nullable=True,
        index=True,
    )

    broker_order_id = Column(
        String,
        nullable=True,
    )

    broker_position_id = Column(
        String,
        nullable=True,
    )

    broker_connection_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    broker_trade_id = Column(
        String,
        nullable=True,
        index=True,
    )

    broker_execution_id = Column(
        String,
        nullable=True,
    )

    broker_account_id = Column(
        String,
        nullable=True,
    )

    broker_server = Column(
        String,
        nullable=True,
    )

    import_source = Column(
        String,
        nullable=True,
    )

    import_job_id = Column(
        Integer,
        nullable=True,
    )

    raw_trade_hash = Column(
        String,
        nullable=True,
        index=True,
    )