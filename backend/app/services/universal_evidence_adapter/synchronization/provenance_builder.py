from __future__ import annotations

"""
Institutional Provenance Builder

The Provenance Builder constructs the complete provenance record for every
piece of evidence synchronized into the Trading Truth Layer (TTL).

Responsibilities
----------------
- Preserve broker identity
- Preserve account identity
- Preserve synchronization identity
- Preserve original provider identifiers
- Compute evidence quality metrics
- Build immutable provenance metadata

The Provenance Builder does NOT:
- Canonicalize evidence
- Verify evidence
- Publish evidence
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.services.universal_evidence_adapter.domain.transport.raw_evidence import (
    RawEvidence,
)


# ============================================================================
# Integrity Scores
# ============================================================================

@dataclass(slots=True)
class IntegrityScores:
    """
    Quality metrics attached to synchronized evidence.
    """

    integrity_score: float = 100.0
    completeness_score: float = 100.0
    authenticity_score: float = 100.0
    synchronization_score: float = 100.0
    canonicalization_score: float = 100.0

    @property
    def overall_score(self) -> float:
        return (
            self.integrity_score +
            self.completeness_score +
            self.authenticity_score +
            self.synchronization_score +
            self.canonicalization_score
        ) / 5.0


# ============================================================================
# Provenance Record
# ============================================================================

@dataclass(slots=True)
class ProvenanceRecord:

    canonical_evidence_id: str

    evidence_hash: str

    provider_name: str

    provider_platform: str

    broker_server: str | None = None

    broker_account_id: str | None = None
    broker_account_name: str | None = None

    account_state: str | None = None
    account_currency: str | None = None

    workspace_id: int | None = None

    synchronization_session: str | None = None
    synchronization_batch: str | None = None
    synchronization_sequence: int | None = None

    original_ticket_id: str | None = None
    original_order_id: str | None = None
    original_deal_id: str | None = None
    original_position_id: str | None = None
    original_execution_id: str | None = None

    received_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    scores: IntegrityScores = field(
        default_factory=IntegrityScores
    )

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Provenance Builder
# ============================================================================

class ProvenanceBuilder:
    """
    Builds institutional provenance records.
    """

    def build(
        self,
        *,
        canonical_evidence_id: str,
        evidence_hash: str,
        provider_name: str,
        provider_platform: str,
        broker_server: str | None = None,
        broker_account_id: str | None = None,
        broker_account_name: str | None = None,
        account_state: str | None = None,
        account_currency: str | None = None,
        workspace_id: int | None = None,
        synchronization_session: str | None = None,
        synchronization_batch: str | None = None,
        synchronization_sequence: int | None = None,
        original_ticket_id: str | None = None,
        original_order_id: str | None = None,
        original_deal_id: str | None = None,
        original_position_id: str | None = None,
        original_execution_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProvenanceRecord:
        """
        Construct a provenance record.
        """

        return ProvenanceRecord(
            canonical_evidence_id=canonical_evidence_id,
            evidence_hash=evidence_hash,
            provider_name=provider_name,
            provider_platform=provider_platform,
            broker_server=broker_server,
            broker_account_id=broker_account_id,
            broker_account_name=broker_account_name,
            account_state=account_state,
            account_currency=account_currency,
            workspace_id=workspace_id,
            synchronization_session=synchronization_session,
            synchronization_batch=synchronization_batch,
            synchronization_sequence=synchronization_sequence,
            original_ticket_id=original_ticket_id,
            original_order_id=original_order_id,
            original_deal_id=original_deal_id,
            original_position_id=original_position_id,
            original_execution_id=original_execution_id,
            metadata=metadata or {},
        )

    def validate(
        self,
        provenance: ProvenanceRecord,
    ) -> list[str]:
        """
        Validate a provenance record.
        """

        issues: list[str] = []

        if not provenance.provider_name:
            issues.append("Provider name is required.")

        if not provenance.provider_platform:
            issues.append("Provider platform is required.")

        if not provenance.evidence_hash:
            issues.append("Evidence hash is required.")

        if not provenance.canonical_evidence_id:
            issues.append("Canonical evidence ID is required.")

        return issues

    def build_from_raw(
        self,
        *,
        canonical_evidence_id: str,
        evidence: RawEvidence,
    ) -> ProvenanceRecord:
        """
        Build provenance directly from RawEvidence.
        """

        return self.build(
            canonical_evidence_id=canonical_evidence_id,
            evidence_hash=evidence.evidence_hash or "",
            provider_name=evidence.provider_name,
            provider_platform=evidence.provider_platform,
            broker_server=evidence.metadata.provider.broker_server,
            broker_account_id=evidence.broker_account_id,
            broker_account_name=evidence.metadata.account.broker_account_name,
            account_state=evidence.account_state,
            account_currency=evidence.metadata.account.account_currency,
            workspace_id=evidence.metadata.workspace.workspace_id,
            synchronization_session=evidence.metadata.synchronization.synchronization_session,
            synchronization_batch=evidence.metadata.synchronization.synchronization_batch,
            synchronization_sequence=evidence.metadata.synchronization.synchronization_sequence,
            original_ticket_id=evidence.provider_ids.ticket_id,
            original_order_id=evidence.provider_ids.order_id,
            original_deal_id=evidence.provider_ids.deal_id,
            original_position_id=evidence.provider_ids.position_id,
            original_execution_id=evidence.provider_ids.execution_id,
        )

    # ----------------------------------------------------------------------

    def process(
        self,
        *,
        canonical_evidence_id: str,
        evidence: RawEvidence,
    ) -> ProvenanceRecord:
        """
        Pipeline entry point.

        Construct institutional provenance.
        """

        return self.build_from_raw(
            canonical_evidence_id=canonical_evidence_id,
            evidence=evidence,
        )


# ============================================================================
# Backwards Compatibility
# ============================================================================

EvidenceProvenanceBuilder = ProvenanceBuilder


__all__ = [
    "IntegrityScores",
    "ProvenanceRecord",
    "ProvenanceBuilder",
    "EvidenceProvenanceBuilder",
]