from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

from app.core.db import Base


class ClaimSchemaPreset(Base):
    __tablename__ = "claim_schema_presets"

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

    name = Column(
        String,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    preset_type = Column(
        String,
        nullable=False,
        default="custom",
    )

    included_member_ids_json = Column(
        Text,
        nullable=False,
        default="[]",
    )

    included_symbols_json = Column(
        Text,
        nullable=False,
        default="[]",
    )

    methodology_notes = Column(
        Text,
        nullable=False,
        default="",
    )

    default_visibility = Column(
        String,
        nullable=False,
        default="private",
    )

    is_system = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    is_active = Column(
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