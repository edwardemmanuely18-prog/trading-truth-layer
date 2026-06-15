from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func

from app.core.db import Base


class SyncJob(Base):
    __tablename__ = "sync_jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    workspace_id = Column(
        Integer,
        ForeignKey("workspaces.id"),
        nullable=False,
        index=True,
    )

    connection_id = Column(
        Integer,
        ForeignKey("broker_connections.id"),
        nullable=False,
        index=True,
    )

    provider = Column(
        String,
        nullable=False,
    )

    sync_type = Column(
        String,
        nullable=False,
        default="incremental",
    )

    status = Column(
        String,
        nullable=False,
        default="queued",
    )

    records_processed = Column(
        Integer,
        nullable=False,
        default=0,
    )

    records_imported = Column(
        Integer,
        nullable=False,
        default=0,
    )

    records_skipped = Column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message = Column(
        String,
        nullable=True,
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
