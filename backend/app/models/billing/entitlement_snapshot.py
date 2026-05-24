from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)

from app.core.db import Base


class EntitlementSnapshot(Base):
    __tablename__ = "entitlement_snapshots"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    plan_code = Column(String, nullable=False)

    limits_json = Column(Text, nullable=False)

    usage_json = Column(Text, nullable=False)

    generated_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )