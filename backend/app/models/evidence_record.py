from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.sql import func

from app.core.db import Base


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

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

    trade_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    import_batch_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    ingestion_session_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    evidence_type = Column(
        String,
        nullable=False,
        default="trade_import",
    )

    evidence_hash = Column(
        String,
        nullable=True,
        index=True,
    )

    evidence_payload_json = Column(
        Text,
        nullable=False,
        default="{}",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )