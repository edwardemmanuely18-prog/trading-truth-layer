from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from app.core.db import Base


class BillingSubscription(Base):
    __tablename__ = "billing_subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(Integer, nullable=False, index=True)

    provider = Column(String, nullable=False)

    provider_customer_id = Column(String, nullable=True)
    provider_subscription_id = Column(String, nullable=True)

    plan_code = Column(String, nullable=False)

    billing_cycle = Column(String, nullable=False)

    status = Column(String, nullable=False)

    current_period_end = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )