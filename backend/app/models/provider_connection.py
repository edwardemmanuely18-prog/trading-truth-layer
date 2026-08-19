"""
Trading Truth Layer (TTL)

Provider Connection Persistence Model

SQLAlchemy persistence model for the canonical ProviderConnection
domain object.

This model is intentionally separate from:

    app.services.provider_connections.models.ProviderConnection

The service/domain model remains the runtime/application representation.

This model exists only for durable database persistence.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    JSON,
    String,
)

from app.core.db import Base


# ============================================================
# Provider Connection
# ============================================================


class ProviderConnectionModel(Base):
    """
    Persistent Provider Connection record.

    This model stores the durable definition required to rebuild
    a RuntimeConnection after application restart, logout/login,
    worker restart, or deployment restart.
    """

    __tablename__ = "provider_connections"

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    workspace_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    connection_name = Column(
        String,
        nullable=False,
    )

    # --------------------------------------------------------
    # Provider / Engine
    # --------------------------------------------------------

    provider = Column(
        String,
        nullable=False,
        index=True,
    )

    engine = Column(
        String,
        nullable=False,
        index=True,
    )

    environment = Column(
        String,
        nullable=False,
        index=True,
    )

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    configuration = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    # --------------------------------------------------------
    # Connection State
    # --------------------------------------------------------

    status = Column(
        String,
        nullable=False,
        default="created",
        index=True,
    )

    health = Column(
        String,
        nullable=False,
        default="unknown",
        index=True,
    )

    verified = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    connected = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    statistics = Column(
        JSON,
        nullable=False,
        default=dict,
    )

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )