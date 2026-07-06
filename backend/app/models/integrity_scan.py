from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
)

from sqlalchemy.sql import func

from app.core.db import Base


class IntegrityScan(Base):
    __tablename__ = "integrity_scans"

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

    status = Column(
        String,
        nullable=False,
        default="valid",
    )

    claims_scanned = Column(
        Integer,
        nullable=False,
        default=0,
    )

    alerts_found = Column(
        Integer,
        nullable=False,
        default=0,
    )

    summary_json = Column(
        Text,
        nullable=True,
    )

    started_at = Column(
        DateTime,
        server_default=func.now(),
    )

    completed_at = Column(
        DateTime,
        nullable=True,
    )