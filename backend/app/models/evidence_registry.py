"""
Trading Truth Layer (TTL)

V2 Evidence Registry Persistence Model

Durable SQLAlchemy representation of the institutional
V2 Evidence Registry.

This model is intentionally separate from the runtime
EvidenceRegistry domain object.
"""

from datetime import datetime, timezone

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Text

from app.core.db import Base


class EvidenceRegistryModel(Base):
    """
    Durable V2 Evidence Registry record.

    The runtime EvidenceRegistry remains responsible for
    synchronization-time registry state.

    This model provides durable persistence across:
    - backend restart
    - process restart
    - deployment restart
    - runtime reconstruction
    """

    __tablename__ = "v2_evidence_registry"

    # ========================================================
    # Canonical Identity
    # ========================================================

    canonical_evidence_id = Column(
        String,
        primary_key=True,
        index=True,
    )

    workspace_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    provider_id = Column(
        String,
        nullable=True,
        index=True,
    )

    # ========================================================
    # Evidence Identity
    # ========================================================

    evidence_type = Column(
        String,
        nullable=False,
        index=True,
    )

    evidence_hash = Column(
        String,
        nullable=False,
        index=True,
    )

    evidence_version = Column(
        Integer,
        nullable=False,
        default=1,
    )

    lifecycle = Column(
        String,
        nullable=False,
        default="REGISTERED",
        index=True,
    )

    # ========================================================
    # Synchronization Lineage
    # ========================================================

    synchronization_batch = Column(
        String,
        nullable=True,
        index=True,
    )

    synchronization_session = Column(
        String,
        nullable=True,
        index=True,
    )

    registered_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # ========================================================
    # Provider Identity
    # ========================================================

    provider_name = Column(
        String,
        nullable=False,
        index=True,
    )

    provider_platform = Column(
        String,
        nullable=False,
        default="unknown",
        index=True,
    )

    broker_server = Column(
        String,
        nullable=True,
        index=True,
    )

    broker_account_id = Column(
        String,
        nullable=True,
        index=True,
    )

    broker_account_name = Column(
        String,
        nullable=True,
    )

    account_state = Column(
        String,
        nullable=True,
        index=True,
    )

    account_currency = Column(
        String,
        nullable=True,
    )

    # ========================================================
    # Original Provider Identifiers
    # ========================================================

    original_ticket_id = Column(
        String,
        nullable=True,
        index=True,
    )

    original_order_id = Column(
        String,
        nullable=True,
        index=True,
    )

    original_deal_id = Column(
        String,
        nullable=True,
        index=True,
    )

    original_position_id = Column(
        String,
        nullable=True,
        index=True,
    )

    original_execution_id = Column(
        String,
        nullable=True,
        index=True,
    )

    # ========================================================
    # Durable Payloads
    # ========================================================

    metadata_payload = Column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )

    canonical_payload = Column(
        JSON,
        nullable=True,
    )

    provenance_payload = Column(
        JSON,
        nullable=True,
    )

    # ========================================================
    # Integrity
    # ========================================================

    payload_hash = Column(
        Text,
        nullable=True,
    )

    evidence_payload_size = Column(
        Integer,
        nullable=True,
    )