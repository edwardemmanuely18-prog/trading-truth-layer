from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)

from datetime import datetime

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

    severity = Column(
        String,
        nullable=False,
        index=True,
    )

    alert_type = Column(
        String,
        nullable=False,
        index=True,
    )

    entity_type = Column(
        String,
        nullable=False,
    )

    entity_id = Column(
        String,
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    summary = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
        default="open",
    )

    acknowledged_at = Column(
        DateTime,
        nullable=True,
    )

    acknowledged_by = Column(
        String,
        nullable=True,
    )

    investigation_notes = Column(
        Text,
        nullable=True,
    )

    resolution_notes = Column(
        Text,
        nullable=True,
    )

    resolved_by = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    resolved_at = Column(
        DateTime,
        nullable=True,
    )