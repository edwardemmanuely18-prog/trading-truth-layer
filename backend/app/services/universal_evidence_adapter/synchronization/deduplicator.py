from __future__ import annotations

"""
Institutional Evidence Deduplicator

The Evidence Deduplicator prevents duplicate evidence from entering the
Trading Truth Layer (TTL).

Responsibilities
----------------
- Detect duplicate evidence
- Register processed evidence fingerprints
- Prevent duplicate synchronization
- Export duplicate metrics
- Validate deduplication state

The deduplicator does NOT:
- Canonicalize evidence
- Verify evidence
- Publish evidence
- Modify evidence
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.services.universal_evidence_adapter.domain.transport.raw_evidence import (
    RawEvidence,
)


# ============================================================================
# Duplicate Record
# ============================================================================

@dataclass(slots=True)
class DuplicateRecord:
    """
    Stores information about processed evidence.
    """

    evidence_hash: str

    provider_name: str

    provider_platform: str

    broker_account_id: str | None

    first_seen: datetime

    last_seen: datetime

    occurrences: int = 1


# ============================================================================
# Deduplication Metrics
# ============================================================================

@dataclass(slots=True)
class DeduplicationMetrics:

    processed: int = 0

    unique: int = 0

    duplicates: int = 0


# ============================================================================
# Evidence Deduplicator
# ============================================================================

class EvidenceDeduplicator:
    """
    Institutional evidence deduplication service.
    """

    def __init__(self) -> None:

        self._records: dict[str, DuplicateRecord] = {}

        self._metrics = DeduplicationMetrics()

    # ------------------------------------------------------------------

    @property
    def metrics(self) -> DeduplicationMetrics:
        return self._metrics

    # ------------------------------------------------------------------

    def exists(
        self,
        evidence_hash: str,
    ) -> bool:
        """
        Returns True if the evidence has already been synchronized.
        """

        return evidence_hash in self._records

    # ------------------------------------------------------------------

    def register(
        self,
        *,
        evidence_hash: str,
        provider_name: str,
        provider_platform: str,
        broker_account_id: str | None = None,
    ) -> DuplicateRecord:
        """
        Register evidence for future duplicate detection.
        """

        self._metrics.processed += 1

        now = datetime.now(timezone.utc)

        existing = self._records.get(evidence_hash)

        if existing is not None:

            existing.last_seen = now
            existing.occurrences += 1

            self._metrics.duplicates += 1

            return existing

        record = DuplicateRecord(
            evidence_hash=evidence_hash,
            provider_name=provider_name,
            provider_platform=provider_platform,
            broker_account_id=broker_account_id,
            first_seen=now,
            last_seen=now,
        )

        self._records[evidence_hash] = record

        self._metrics.unique += 1

        return record

    # ------------------------------------------------------------------

    def should_process(
        self,
        evidence_hash: str,
    ) -> bool:
        """
        Determines whether evidence should continue through the pipeline.
        """

        return evidence_hash not in self._records

    # ------------------------------------------------------------------

    def get(
        self,
        evidence_hash: str,
    ) -> DuplicateRecord | None:

        return self._records.get(evidence_hash)

    # ------------------------------------------------------------------

    def remove(
        self,
        evidence_hash: str,
    ) -> bool:
        """
        Remove an evidence fingerprint.
        """

        if evidence_hash not in self._records:
            return False

        del self._records[evidence_hash]

        self._metrics.unique -= 1

        return True

    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Clear deduplication cache.
        """

        self._records.clear()

        self._metrics = DeduplicationMetrics()

    # ------------------------------------------------------------------

    def records(self) -> list[DuplicateRecord]:

        return list(self._records.values())

    # ------------------------------------------------------------------

    def statistics(self) -> dict[str, Any]:

        duplicate_rate = 0.0

        if self._metrics.processed > 0:
            duplicate_rate = (
                self._metrics.duplicates /
                self._metrics.processed
            )

        return {
            "processed": self._metrics.processed,
            "unique": self._metrics.unique,
            "duplicates": self._metrics.duplicates,
            "duplicate_rate": duplicate_rate,
            "stored_hashes": len(self._records),
        }

    # ------------------------------------------------------------------

    def validate(self) -> list[str]:
        """
        Validate deduplication state.
        """

        issues: list[str] = []

        if self._metrics.processed < 0:
            issues.append(
                "Processed count cannot be negative."
            )

        if self._metrics.unique < 0:
            issues.append(
                "Unique count cannot be negative."
            )

        if self._metrics.duplicates < 0:
            issues.append(
                "Duplicate count cannot be negative."
            )

        if len(self._records) != self._metrics.unique:
            issues.append(
                "Stored record count does not match unique metric."
            )

        return issues

    def should_process_evidence(
        self,
        evidence: RawEvidence,
    ) -> bool:
        """
        Determine whether the supplied RawEvidence should continue
        through the synchronization pipeline.
        """

        evidence_hash = evidence.evidence_hash

        if evidence_hash is None:
            raise ValueError(
                "RawEvidence does not contain an evidence hash."
            )

        return self.should_process(evidence_hash)

    # ------------------------------------------------------------------

    def process(
        self,
        evidence: RawEvidence,
    ) -> bool:
        """
        Pipeline entry point.

        Returns True if the evidence should continue
        through synchronization.
        """

        return self.should_process_evidence(evidence)