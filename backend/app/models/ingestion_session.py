from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

from app.core.db import Base


class IngestionSession(Base):
    __tablename__ = "ingestion_sessions"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    actor_user_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    source_type = Column(
        String,
        nullable=False,
        index=True,
    )

    source_name = Column(
        String,
        nullable=True,
    )

    ingestion_mode = Column(
        String,
        nullable=False,
        default="manual",
    )

    session_status = Column(
        String,
        nullable=False,
        default="completed",
    )

    rows_received = Column(
        Integer,
        nullable=False,
        default=0,
    )

    rows_imported = Column(
        Integer,
        nullable=False,
        default=0,
    )

    rows_rejected = Column(
        Integer,
        nullable=False,
        default=0,
    )

    rows_skipped_duplicates = Column(
        Integer,
        nullable=False,
        default=0,
    )

    ingestion_fingerprint = Column(
        String,
        nullable=True,
        index=True,
    )

    diagnostic_summary = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )