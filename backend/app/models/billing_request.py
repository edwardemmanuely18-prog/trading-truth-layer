from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text

from app.core.db import Base


class BillingRequest(Base):
    __tablename__ = "billing_requests"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(Integer, nullable=False, index=True)
    requested_by_user_id = Column(Integer, nullable=False)

    current_plan_code = Column(String, nullable=False)
    target_plan_code = Column(String, nullable=False)
    billing_cycle = Column(String, nullable=False)  # monthly / annual

    amount_usd = Column(Integer, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="pending",  # pending | paid | approved | rejected
    )

    payment_reference = Column(String, nullable=True)
    payment_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )