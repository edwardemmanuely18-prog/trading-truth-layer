from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)

from app.core.db import Base


class IntegrityAlert(Base):
    __tablename__ = "integrity_alerts"

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

    claim_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    alert_type = Column(
        String,
        nullable=False,
        index=True,
    )

    severity = Column(
        String,
        nullable=False,
        default="warning",
    )

    status = Column(
        String,
        nullable=False,
        default="open",
    )

    summary = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )