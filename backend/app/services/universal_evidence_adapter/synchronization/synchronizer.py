from __future__ import annotations

"""
Institutional Evidence Synchronizer

Coordinates synchronization of broker-neutral RawEvidence through the
Universal Evidence Adapter (UEA).

Responsibilities
----------------
- Receive RawEvidence from the Desktop Trading Engine
- Buffer evidence
- Eliminate duplicates
- Register evidence
- Build provenance
- Canonicalize evidence
- Publish canonical evidence
- Collect synchronization metrics
- Produce synchronization reports

The synchronizer performs orchestration only.

Business logic remains inside the synchronization stages.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable
from uuid import uuid4

from app.services.universal_evidence_adapter.domain.transport.raw_evidence import (
    RawEvidence,
)
from app.services.universal_evidence_adapter.synchronization.canonicalizer import (
    CanonicalEvidence,
)
from app.services.universal_evidence_adapter.synchronization.evidence_buffer import (
    BufferEntry,
    EvidenceBuffer,
)
from app.services.universal_evidence_adapter.synchronization.deduplicator import (
    EvidenceDeduplicator,
)
from app.services.universal_evidence_adapter.synchronization.evidence_registry import (
    EvidenceRegistry,
    EvidenceRegistryRecord,
)
from app.services.universal_evidence_adapter.synchronization.provenance_builder import (
    EvidenceProvenanceBuilder,
    ProvenanceRecord,
)
from app.services.universal_evidence_adapter.synchronization.publisher import (
    EvidencePublisher,
    PublishResult,
)


# ============================================================================
# Synchronization Status
# ============================================================================


class SynchronizationStatus(str, Enum):

    SUCCESS = "SUCCESS"

    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"

    FAILED = "FAILED"

    CANCELLED = "CANCELLED"


# ============================================================================
# Synchronization Error
# ============================================================================


@dataclass(slots=True)
class SynchronizationError:
    """
    Represents one synchronization failure.
    """

    evidence_hash: str | None

    provider_name: str | None

    broker_account_id: str | None

    stage: str

    error: str

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================================
# Synchronization Metrics
# ============================================================================


@dataclass(slots=True)
class SynchronizationMetrics:

    received: int = 0

    buffered: int = 0

    processed: int = 0

    duplicates: int = 0

    registered: int = 0

    canonicalized: int = 0

    published: int = 0

    failed: int = 0

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float = 0.0

    @property
    def successful(self) -> int:
        return self.processed - self.failed

    @property
    def success_rate(self) -> float:

        if self.processed == 0:
            return 0.0

        return (self.successful / self.processed) * 100.0


# ============================================================================
# Synchronization Result
# ============================================================================


@dataclass(slots=True)
class SynchronizationResult:

    synchronization_id: str

    status: SynchronizationStatus

    metrics: SynchronizationMetrics

    published: list[CanonicalEvidence] = field(
        default_factory=list
    )

    publish_results: list[PublishResult] = field(
        default_factory=list
    )

    registry_records: list[EvidenceRegistryRecord] = field(
        default_factory=list
    )

    provenance_records: list[ProvenanceRecord] = field(
        default_factory=list
    )

    buffered_entries: list[BufferEntry] = field(
        default_factory=list
    )

    errors: list[SynchronizationError] = field(
        default_factory=list
    )

    @property
    def succeeded(self) -> bool:
        return self.status == SynchronizationStatus.SUCCESS

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def add_error(
        self,
        *,
        evidence: RawEvidence | None,
        stage: str,
        error: Exception,
    ) -> None:

        self.errors.append(
            SynchronizationError(
                evidence_hash=(
                    evidence.evidence_hash
                    if evidence else None
                ),
                provider_name=(
                    evidence.provider_name
                    if evidence else None
                ),
                broker_account_id=(
                    evidence.broker_account_id
                    if evidence else None
                ),
                stage=stage,
                error=str(error),
            )
        )

        self.metrics.failed += 1


# ============================================================================
# Internal Synchronization Context
# ============================================================================


@dataclass(slots=True)
class SynchronizationContext:

    raw: RawEvidence

    canonical_evidence_id: str

    buffer_entry: BufferEntry | None = None

    registry_record: EvidenceRegistryRecord | None = None

    provenance: ProvenanceRecord | None = None

    canonical: CanonicalEvidence | None = None


# ============================================================================
# Evidence Synchronizer
# ============================================================================


class EvidenceSynchronizer:
    """
    Institutional synchronization orchestrator.

    Coordinates RawEvidence through the complete
    Universal Evidence Adapter synchronization pipeline.

    The synchronizer owns orchestration only.

    Business logic remains inside the individual
    synchronization stages.
    """

    def __init__(
        self,
        *,
        buffer: EvidenceBuffer,
        deduplicator: EvidenceDeduplicator,
        registry: EvidenceRegistry,
        provenance_builder: EvidenceProvenanceBuilder,
        canonicalizer: EvidenceCanonicalizer,
        publisher: EvidencePublisher,
    ) -> None:

        self._buffer = buffer
        self._deduplicator = deduplicator
        self._registry = registry
        self._provenance_builder = provenance_builder
        self._canonicalizer = canonicalizer
        self._publisher = publisher

    # ------------------------------------------------------------------

    @property
    def buffer(self) -> EvidenceBuffer:
        return self._buffer

    @property
    def deduplicator(self) -> EvidenceDeduplicator:
        return self._deduplicator

    @property
    def registry(self) -> EvidenceRegistry:
        return self._registry

    @property
    def provenance_builder(
        self,
    ) -> EvidenceProvenanceBuilder:
        return self._provenance_builder

    @property
    def canonicalizer(
        self,
    ) -> EvidenceCanonicalizer:
        return self._canonicalizer

    @property
    def publisher(
        self,
    ) -> EvidencePublisher:
        return self._publisher

    # ------------------------------------------------------------------

    def validate_dependencies(self) -> list[str]:
        """
        Validate that all synchronization stages
        are available.
        """

        issues: list[str] = []

        if self._buffer is None:
            issues.append("EvidenceBuffer is missing.")

        if self._deduplicator is None:
            issues.append("EvidenceDeduplicator is missing.")

        if self._registry is None:
            issues.append("EvidenceRegistry is missing.")

        if self._provenance_builder is None:
            issues.append("ProvenanceBuilder is missing.")

        if self._canonicalizer is None:
            issues.append("EvidenceCanonicalizer is missing.")

        if self._publisher is None:
            issues.append("EvidencePublisher is missing.")

        return issues

    # ------------------------------------------------------------------

    def _new_synchronization_id(self) -> str:
        """
        Generate a synchronization execution ID.
        """

        return str(uuid4())

    # ------------------------------------------------------------------

    def _new_canonical_evidence_id(self) -> str:
        """
        Generate a canonical evidence identifier.
        """

        return str(uuid4())

    # ------------------------------------------------------------------

    def _new_context(
        self,
        evidence: RawEvidence,
    ) -> SynchronizationContext:
        """
        Create synchronization context.
        """

        return SynchronizationContext(
            raw=evidence,
            canonical_evidence_id=self._new_canonical_evidence_id(),
        )

    # ------------------------------------------------------------------

    def _start_metrics(
        self,
        metrics: SynchronizationMetrics,
    ) -> None:

        metrics.started_at = datetime.now(timezone.utc)

    # ------------------------------------------------------------------

    def _finish_metrics(
        self,
        metrics: SynchronizationMetrics,
        *,
        started: float,
    ) -> None:

        metrics.completed_at = datetime.now(timezone.utc)

        metrics.duration_seconds = (
            time.perf_counter() - started
        )

    # ------------------------------------------------------------------

    def _determine_status(
        self,
        metrics: SynchronizationMetrics,
    ) -> SynchronizationStatus:

        if metrics.processed == 0:
            return SynchronizationStatus.FAILED

        if metrics.failed == 0:
            return SynchronizationStatus.SUCCESS

        if metrics.successful == 0:
            return SynchronizationStatus.FAILED

        return SynchronizationStatus.PARTIAL_SUCCESS

    # ------------------------------------------------------------------

    def _validate_raw_evidence(
        self,
        evidence: RawEvidence,
    ) -> None:
        """
        Validate transport object before entering
        the synchronization pipeline.
        """

        issues = evidence.validate()

        if issues:
            raise ValueError(
                "; ".join(issues)
            )

    # ------------------------------------------------------------------

    def _buffer_evidence(
        self,
        context: SynchronizationContext,
        metrics: SynchronizationMetrics,
    ) -> None:
        """
        Buffer incoming evidence.
        """

        context.buffer_entry = self.buffer.process(
            context.raw
        )

        metrics.buffered += 1

    # ------------------------------------------------------------------

    def _is_duplicate(
        self,
        context: SynchronizationContext,
        metrics: SynchronizationMetrics,
    ) -> bool:
        """
        Determine whether the supplied evidence
        has already been synchronized.
        """

        should_continue = (
            self.deduplicator.process(
                context.raw
            )
        )

        if not should_continue:
            metrics.duplicates += 1
            return True

        return False

    # ------------------------------------------------------------------

    def _register(
        self,
        context: SynchronizationContext,
        metrics: SynchronizationMetrics,
    ) -> None:

        context.registry_record = (
            self.registry.process(
                context.raw
            )
        )

        metrics.registered += 1

    # ------------------------------------------------------------------

    def _build_provenance(
        self,
        context: SynchronizationContext,
    ) -> None:

        context.provenance = (
            self.provenance_builder.process(
                canonical_evidence_id=(
                    context.canonical_evidence_id
                ),
                evidence=context.raw,
            )
        )

    # ------------------------------------------------------------------

    def _canonicalize(
        self,
        context: SynchronizationContext,
        metrics: SynchronizationMetrics,
    ) -> None:

        context.canonical = (
            self.canonicalizer.process(
                evidence=context.raw,
                canonical_evidence_id=(
                    context.canonical_evidence_id
                ),
                provenance=context.provenance,
            )
        )

        metrics.canonicalized += 1

    # ------------------------------------------------------------------

    def _publish(
        self,
        context: SynchronizationContext,
        result: SynchronizationResult,
        metrics: SynchronizationMetrics,
    ) -> None:

        publish_results = (
            self.publisher.process(
                context.canonical
            )
        )

        result.publish_results.extend(
            publish_results
        )

        result.published.append(
            context.canonical
        )

        successful_publications = sum(
            1
            for result in publish_results
            if result.success
        )

        metrics.published += successful_publications

    # ------------------------------------------------------------------

    def synchronize_one(
        self,
        evidence: RawEvidence,
    ) -> SynchronizationResult:
        """
        Synchronize a single RawEvidence object through the
        complete Universal Evidence Adapter pipeline.

        The pipeline consists of:

            Validate
                ↓
            Buffer
                ↓
            Deduplicate
                ↓
            Registry
                ↓
            Provenance
                ↓
            Canonicalization
                ↓
            Publication
        """

        dependency_issues = self.validate_dependencies()

        if dependency_issues:
            raise RuntimeError(
                "Synchronization dependencies are invalid: "
                + "; ".join(dependency_issues)
            )

        started = time.perf_counter()

        metrics = SynchronizationMetrics()

        self._start_metrics(metrics)

        metrics.received = 1

        result = SynchronizationResult(
            synchronization_id=self._new_synchronization_id(),
            status=SynchronizationStatus.SUCCESS,
            metrics=metrics,
        )

        context = self._new_context(evidence)

        try:

            # ----------------------------------------------------------
            # Validate transport
            # ----------------------------------------------------------

            self._validate_raw_evidence(
                context.raw
            )

            # ----------------------------------------------------------
            # Buffer
            # ----------------------------------------------------------

            self._buffer_evidence(
                context,
                metrics,
            )

            result.buffered_entries.append(
                context.buffer_entry
            )

            # ----------------------------------------------------------
            # Duplicate Detection
            # ----------------------------------------------------------

            if self._is_duplicate(
                context,
                metrics,
            ):

                metrics.processed += 1

                self._finish_metrics(
                    metrics,
                    started=started,
                )

                result.status = (
                    self._determine_status(
                        metrics
                    )
                )

                return result

            # ----------------------------------------------------------
            # Registry
            # ----------------------------------------------------------

            self._register(
                context,
                metrics,
            )

            result.registry_records.append(
                context.registry_record
            )

            # ----------------------------------------------------------
            # Provenance
            # ----------------------------------------------------------

            self._build_provenance(
                context
            )

            result.provenance_records.append(
                context.provenance
            )

            # ----------------------------------------------------------
            # Canonicalization
            # ----------------------------------------------------------

            self._canonicalize(
                context,
                metrics,
            )

            # ----------------------------------------------------------
            # Publication
            # ----------------------------------------------------------

            self._publish(
                context,
                result,
                metrics,
            )

            metrics.processed += 1

        except Exception as exc:

            result.add_error(
                evidence=evidence,
                stage="Synchronization",
                error=exc,
            )

        finally:

            self._finish_metrics(
                metrics,
                started=started,
            )

            result.status = (
                self._determine_status(
                    metrics
                )
            )

        return result

    # ------------------------------------------------------------------

    def synchronize_batch(
        self,
        evidences: Iterable[RawEvidence],
    ) -> SynchronizationResult:
        """
        Synchronize a batch of RawEvidence objects.

        Each evidence item is processed independently.
        Failures do not interrupt the remaining batch.
        """

        dependency_issues = self.validate_dependencies()

        if dependency_issues:
            raise RuntimeError(
                "Synchronization dependencies are invalid: "
                + "; ".join(dependency_issues)
            )

        started = time.perf_counter()

        metrics = SynchronizationMetrics()

        self._start_metrics(metrics)

        synchronization_id = self._new_synchronization_id()

        result = SynchronizationResult(
            synchronization_id=synchronization_id,
            status=SynchronizationStatus.SUCCESS,
            metrics=metrics,
        )

        for evidence in evidences:

            metrics.received += 1

            item_result = self.synchronize_one(
                evidence
            )

            metrics.buffered += (
                item_result.metrics.buffered
            )

            metrics.processed += (
                item_result.metrics.processed
            )

            metrics.duplicates += (
                item_result.metrics.duplicates
            )

            metrics.registered += (
                item_result.metrics.registered
            )

            metrics.canonicalized += (
                item_result.metrics.canonicalized
            )

            metrics.published += (
                item_result.metrics.published
            )

            metrics.failed += (
                item_result.metrics.failed
            )

            result.publish_results.extend(
                item_result.publish_results
            )

            result.registry_records.extend(
                item_result.registry_records
            )

            result.provenance_records.extend(
                item_result.provenance_records
            )

            result.buffered_entries.extend(
                item_result.buffered_entries
            )

            result.published.extend(
                item_result.published
            )

            result.errors.extend(
                item_result.errors
            )

        self._finish_metrics(
            metrics,
            started=started,
        )

        result.status = (
            self._determine_status(
                metrics
            )
        )

        return result

    # ------------------------------------------------------------------

    def synchronize_stream(
        self,
        stream: Iterable[RawEvidence],
    ) -> SynchronizationResult:
        """
        Synchronize an evidence stream.

        The default implementation simply consumes the
        stream sequentially.

        Future versions may introduce asynchronous,
        event-driven or parallel synchronization without
        changing this public interface.
        """

        return self.synchronize_batch(stream)