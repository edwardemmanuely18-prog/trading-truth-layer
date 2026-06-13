from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from app.core.db import Base


class IntegrityRegistry(Base):
    __tablename__ = "integrity_registry"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    trade_id = Column(
        Integer,
        ForeignKey("trades.id"),
        nullable=False,
        index=True,
    )

    evidence_record_id = Column(
        Integer,
        ForeignKey("evidence_records.id"),
        nullable=True,
        index=True,
    )

    integrity_status = Column(
        String,
        nullable=False,
        default="verified",
    )

    integrity_hash = Column(
        String,
        nullable=False,
        index=True,
    )

    verification_source = Column(
        String,
        nullable=True,
    )

    last_verified_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )