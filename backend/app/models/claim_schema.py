from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.db import Base


class ClaimSchema(Base):
    __tablename__ = "claim_schemas"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, nullable=False, index=True)

    name = Column(String, nullable=False)
    period_start = Column(String, nullable=False)
    period_end = Column(String, nullable=False)

    included_member_ids_json = Column(Text, nullable=False, default="[]")
    included_symbols_json = Column(Text, nullable=False, default="[]")
    excluded_trade_ids_json = Column(Text, nullable=False, default="[]")
    methodology_notes = Column(Text, nullable=False, default="")

    status = Column(String, nullable=False, default="draft")
    visibility = Column(String, nullable=False, default="private")

    parent_claim_id = Column(Integer, nullable=True)
    root_claim_id = Column(Integer, nullable=True)
    version_number = Column(Integer, nullable=False, default=1)

    verified_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    locked_at = Column(DateTime, nullable=True)

    locked_trade_set_hash = Column(String, nullable=True)
    locked_trade_ids_json = Column(Text, nullable=False, default="[]")