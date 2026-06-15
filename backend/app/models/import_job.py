from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.sql import func

from app.core.db import Base


class ImportJob(Base):
    __tablename__ = "import_jobs"

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

    adapter_provider = Column(
        String,
        nullable=False,
    )

    filename = Column(
        String,
        nullable=False,
    )

    file_type = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
        default="uploaded",
    )

    records_detected = Column(
        Integer,
        nullable=False,
        default=0,
    )

    imported_records = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )