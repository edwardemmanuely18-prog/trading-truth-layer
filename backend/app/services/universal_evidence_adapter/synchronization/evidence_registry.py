from __future__ import annotations

"""
Institutional Evidence Registry

The Evidence Registry is responsible for assigning and maintaining the
institutional identity of every evidence synchronized into TTL.

Responsibilities
----------------
- Register canonical evidence
- Preserve provider identity
- Preserve canonical identity
- Maintain evidence lifecycle
- Expose lookup operations
- Export registry metrics

The registry does NOT:

- Deduplicate evidence
- Verify evidence
- Canonicalize evidence
- Publish evidence

Those responsibilities belong to other synchronization components.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from app.services.universal_evidence_adapter.domain.transport.raw_evidence import (
    RawEvidence,
)


# ============================================================================
# Evidence Lifecycle
# ============================================================================

class EvidenceLifecycle(str, Enum):
    REGISTERED = "REGISTERED"
    CANONICALIZED = "CANONICALIZED"
    VERIFIED = "VERIFIED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


# ============================================================================
# Provider Identity
# ============================================================================

@dataclass(slots=True)
class ProviderIdentity:
    """
    Original broker/provider identity.
    """

    provider_name: str
    provider_platform: str

    broker_server: str | None = None

    broker_account_id: str | None = None
    broker_account_name: str | None = None

    account_state: str | None = None      # LIVE / DEMO
    account_currency: str | None = None

    original_ticket_id: str | None = None
    original_deal_id: str | None = None
    original_order_id: str | None = None
    original_position_id: str | None = None
    original_execution_id: str | None = None


# ============================================================================
# Registry Record
# ============================================================================

@dataclass(slots=True)
class EvidenceRegistryRecord:

    canonical_evidence_id: str

    provider: ProviderIdentity

    workspace_id: int | None

    provider_id: str | None

    evidence_hash: str

    evidence_type: str

    evidence_version: int = 1

    lifecycle: EvidenceLifecycle = EvidenceLifecycle.REGISTERED

    synchronization_batch: str | None = None

    synchronization_session: str | None = None

    registered_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Registry Metrics
# ============================================================================

@dataclass(slots=True)
class RegistryMetrics:

    total_registered: int = 0

    active_records: int = 0

    archived_records: int = 0


# ============================================================================
# Evidence Registry
# ============================================================================

class EvidenceRegistry:
    """
    Institutional evidence registry.
    """

    def __init__(self) -> None:

        self._records: dict[str, EvidenceRegistryRecord] = {}

        self._provider_hash_index: dict[str, str] = {}

        self._metrics = RegistryMetrics()

    # ----------------------------------------------------------------------

    @property
    def metrics(self) -> RegistryMetrics:
        return self._metrics

    # ----------------------------------------------------------------------

    def register(
        self,
        *,
        provider: ProviderIdentity,
        evidence_hash: str,
        evidence_type: str,
        workspace_id: int | None = None,
        provider_id: str | None = None,
        synchronization_batch: str | None = None,
        synchronization_session: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvidenceRegistryRecord:
        """
        Register new evidence.
        """

        canonical_id = f"CE-{uuid4().hex.upper()}"

        record = EvidenceRegistryRecord(
            canonical_evidence_id=canonical_id,
            provider=provider,
            workspace_id=workspace_id,
            provider_id=provider_id,
            evidence_hash=evidence_hash,
            evidence_type=evidence_type,
            synchronization_batch=synchronization_batch,
            synchronization_session=synchronization_session,
            metadata=metadata or {},
        )

        self._records[canonical_id] = record

        self._provider_hash_index[evidence_hash] = canonical_id

        self._metrics.total_registered += 1
        self._metrics.active_records += 1

        return record

    # ----------------------------------------------------------------------

    def get(
        self,
        canonical_evidence_id: str,
    ) -> EvidenceRegistryRecord | None:

        return self._records.get(canonical_evidence_id)

    # ----------------------------------------------------------------------

    def get_by_hash(
        self,
        evidence_hash: str,
    ) -> EvidenceRegistryRecord | None:

        canonical_id = self._provider_hash_index.get(evidence_hash)

        if canonical_id is None:
            return None

        return self.get(canonical_id)

    # ----------------------------------------------------------------------

    def exists(
        self,
        evidence_hash: str,
    ) -> bool:

        return evidence_hash in self._provider_hash_index

    # ----------------------------------------------------------------------

    def update_lifecycle(
        self,
        canonical_evidence_id: str,
        lifecycle: EvidenceLifecycle,
    ) -> None:

        record = self.get(canonical_evidence_id)

        if record is None:
            raise KeyError(
                f"Evidence '{canonical_evidence_id}' does not exist."
            )

        record.lifecycle = lifecycle

    # ----------------------------------------------------------------------

    def archive(
        self,
        canonical_evidence_id: str,
    ) -> None:

        record = self.get(canonical_evidence_id)

        if record is None:
            raise KeyError(
                f"Evidence '{canonical_evidence_id}' does not exist."
            )

        record.lifecycle = EvidenceLifecycle.ARCHIVED

        self._metrics.archived_records += 1
        self._metrics.active_records -= 1

    # ----------------------------------------------------------------------

    def records(self) -> list[EvidenceRegistryRecord]:

        return list(self._records.values())

    # ----------------------------------------------------------------------

    def statistics(self) -> dict[str, Any]:

        return {
            "registered": self._metrics.total_registered,
            "active": self._metrics.active_records,
            "archived": self._metrics.archived_records,
        }

    # ----------------------------------------------------------------------

    def validate(self) -> list[str]:
        """
        Validate registry consistency.
        """

        issues: list[str] = []

        if self._metrics.active_records < 0:
            issues.append(
                "Active record count cannot be negative."
            )

        if self._metrics.archived_records < 0:
            issues.append(
                "Archived record count cannot be negative."
            )

        if self._metrics.total_registered < (
            self._metrics.active_records +
            self._metrics.archived_records
        ):
            issues.append(
                "Registry metrics are inconsistent."
            )

        return issues

    def register_evidence(
        self,
        evidence: RawEvidence,
    ) -> EvidenceRegistryRecord:
        """
        Register RawEvidence using its transport metadata.
        """

        evidence_hash = evidence.evidence_hash

        if evidence_hash is None:
            raise ValueError(
                "RawEvidence does not contain an evidence hash."
            )

        return self.register(
            provider=ProviderIdentity(
                provider_name=evidence.provider_name,
                provider_platform=evidence.provider_platform,
                broker_server=evidence.metadata.provider.broker_server,
                broker_account_id=evidence.broker_account_id,
                broker_account_name=evidence.metadata.account.broker_account_name,
                account_state=evidence.account_state,
                account_currency=evidence.metadata.account.account_currency,
                original_ticket_id=evidence.provider_ids.ticket_id,
                original_deal_id=evidence.provider_ids.deal_id,
                original_order_id=evidence.provider_ids.order_id,
                original_position_id=evidence.provider_ids.position_id,
                original_execution_id=evidence.provider_ids.execution_id,
            ),
            evidence_hash=evidence_hash,
            evidence_type=(
                evidence.evidence_type.value
                if hasattr(evidence.evidence_type, "value")
                else str(evidence.evidence_type)
            ),
            workspace_id=evidence.metadata.workspace.workspace_id,
            provider_id=evidence.metadata.workspace.provider_id,
            synchronization_batch=evidence.metadata.synchronization.synchronization_batch,
            synchronization_session=evidence.metadata.synchronization.synchronization_session,
        )

    # ----------------------------------------------------------------------

    def process(
        self,
        evidence: RawEvidence,
    ) -> EvidenceRegistryRecord:
        """
        Pipeline entry point.

        Register evidence inside the institutional registry.
        """

        return self.register_evidence(evidence)