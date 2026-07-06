from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.sql import func

from app.core.db import Base


class ReviewStatement(Base):
    __tablename__ = "review_statements"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    workspace_id = Column(
        Integer,
        ForeignKey("workspaces.id"),
        nullable=False,
        index=True,
    )

    claim_schema_id = Column(
        Integer,
        ForeignKey(
            "claim_schemas.id"
        ),
        nullable=False,
        index=True,
    )

    reviewer_name = Column(
        String,
        nullable=False,
    )

    reviewer_organization = Column(
        String,
        nullable=True,
    )

    reviewer_role = Column(
        String,
        nullable=False,
        index=True,
    )

    observation_type = Column(
        String,
        nullable=False,
        index=True,
    )

    statement = Column(
        Text,
        nullable=False,
    )

    rating = Column(
        Integer,
        nullable=True,
    )

    review_direction = Column(
        String,
        nullable=False,
        default="NEUTRAL",
        index=True,
    )

    status = Column(
        String,
        nullable=False,
        default="ACTIVE",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )