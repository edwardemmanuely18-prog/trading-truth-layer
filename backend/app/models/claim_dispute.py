from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.core.db import Base


class ClaimDispute(Base):
    __tablename__ = "claim_disputes"

    id = Column(Integer, primary_key=True, index=True)

    claim_schema_id = Column(Integer, nullable=False, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)

    status = Column(String, nullable=False, default="open")
    challenge_type = Column(String, nullable=False, default="general_review")
    reason_code = Column(String, nullable=False, default="other")

    summary = Column(String, nullable=False)
    evidence_note = Column(Text, nullable=False, default="")
    reporter_user_id = Column(Integer, nullable=False, index=True)

    reviewer_user_id = Column(Integer, nullable=True, index=True)
    resolution_note = Column(Text, nullable=True)

    opened_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    resolved_at = Column(DateTime, nullable=True)