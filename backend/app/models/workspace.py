from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.core.db import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    description = Column(String, nullable=True)
    billing_email = Column(String, nullable=True)

    plan_code = Column(String, nullable=False, default="starter")
    billing_status = Column(String, nullable=False, default="inactive")
    billing_provider = Column(String, nullable=True)

    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)

    paddle_customer_id = Column(String, nullable=True)
    paddle_subscription_id = Column(String, nullable=True)
    paddle_transaction_id = Column(String, nullable=True)
    paddle_price_id = Column(String, nullable=True)

    subscription_current_period_end = Column(DateTime, nullable=True)

    claim_limit = Column(Integer, nullable=False, default=5)
    trade_limit = Column(Integer, nullable=False, default=1000)
    member_limit = Column(Integer, nullable=False, default=3)
    storage_limit_mb = Column(Integer, nullable=False, default=500)

    trades_consumed_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )