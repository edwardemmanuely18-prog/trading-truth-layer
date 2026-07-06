from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)

from sqlalchemy.sql import func

from app.core.db import Base


class ReportGeneration(Base):
    __tablename__ = "report_generations"

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

    report_type = Column(
        String,
        nullable=False,
        index=True,
    )

    generated_by = Column(
        String,
        nullable=True,
    )

    report_hash = Column(
        String,
        nullable=False,
        index=True,
    )

    status = Column(
        String,
        nullable=False,
        default="generated",
    )

    verification_url = Column(
        Text,
        nullable=True,
    )

    file_name = Column(
        String,
        nullable=True,
    )

    metadata_json = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )