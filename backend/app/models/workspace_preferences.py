from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from app.core.db import Base


class WorkspacePreferences(Base):
    __tablename__ = "workspace_preferences"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    workspace_id = Column(
        Integer,
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    timezone = Column(
        String,
        nullable=False,
        default="UTC",
    )

    language = Column(
        String,
        nullable=False,
        default="English",
    )

    currency = Column(
        String,
        nullable=False,
        default="USD",
    )

    date_format = Column(
        String,
        nullable=False,
        default="YYYY-MM-DD",
    )

    auto_refresh = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    auto_save = Column(
        Boolean,
        nullable=False,
        default=True,
    )

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