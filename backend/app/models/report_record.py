from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from sqlalchemy.sql import func

from app.core.db import Base


class ReportRecord(Base):

    __tablename__ = "report_records"

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

    claim_schema_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    report_type = Column(
        String,
        nullable=False,
        index=True,
    )

    report_hash = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    report_status = Column(
        String,
        nullable=False,
        default="generated",
    )

    generated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )