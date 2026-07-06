from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
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

    evidence_id = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    evidence_type = Column(
        String,
        nullable=False,
        index=True,
    )

    source_type = Column(
        String,
        nullable=False,
        index=True,
    )

    source_reference = Column(
        String,
        nullable=True,
        index=True,
    )

    verification_state = Column(
        String,
        nullable=False,
        default="verified",
    )

    trust_tier = Column(
        String,
        nullable=False,
        default="tier_3",
    )

    sha256_hash = Column(
        String,
        nullable=True,
    )

    fingerprint = Column(
        String,
        nullable=True,
    )

    title = Column(
        String,
        nullable=True,
    )

    metadata_json = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )