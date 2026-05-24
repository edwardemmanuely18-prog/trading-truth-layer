from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)

from app.core.db import Base


class BillingEvent(Base):
    __tablename__ = "billing_events"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(Integer, nullable=True, index=True)

    provider = Column(String, nullable=False)

    provider_event_id = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    event_type = Column(String, nullable=False)

    payload_json = Column(Text, nullable=False)

    event_hash = Column(String, nullable=False)

    processed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )