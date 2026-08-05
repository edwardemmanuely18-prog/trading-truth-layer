from __future__ import annotations

"""
Institutional Evidence Buffer

The Evidence Buffer is the first synchronization component inside the
Universal Evidence Adapter.

Responsibilities
----------------

1. Receive standardized evidence from Desktop Trading Engine.

2. Temporarily buffer evidence before synchronization.

3. Preserve arrival order.

4. Support batch synchronization.

5. Support replay.

6. Provide synchronization metrics.

The buffer intentionally contains NO business logic.

It does NOT:

- canonicalize evidence
- deduplicate evidence
- verify evidence
- publish evidence

Those responsibilities belong to downstream components.
"""

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.services.universal_evidence_adapter.domain.transport.raw_evidence import (
    RawEvidence,
)


# ============================================================================
# Buffer Entry
# ============================================================================

@dataclass(slots=True)
class BufferEntry:
    """
    One buffered evidence object.
    """

    evidence: RawEvidence

    received_at: datetime

    sequence: int


# ============================================================================
# Buffer Metrics
# ============================================================================

@dataclass(slots=True)
class BufferMetrics:
    """
    Runtime buffer statistics.
    """

    current_size: int = 0

    total_received: int = 0

    total_removed: int = 0

    peak_size: int = 0

    batches_processed: int = 0


# ============================================================================
# Evidence Buffer
# ============================================================================

class EvidenceBuffer:
    """
    FIFO institutional evidence buffer.

    Every evidence entering TTL first passes through this buffer.

    Characteristics

        FIFO

        Thread-safe orchestration can be added later.

        Provider independent.

        Broker independent.

        Stores standardized evidence only.
    """

    def __init__(self) -> None:

        self._queue: deque[BufferEntry] = deque()

        self._sequence = 0

        self._metrics = BufferMetrics()

    # ----------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._queue)

    # ----------------------------------------------------------------------

    @property
    def metrics(self) -> BufferMetrics:
        return self._metrics

    # ----------------------------------------------------------------------

    @property
    def empty(self) -> bool:
        return len(self._queue) == 0

    # ----------------------------------------------------------------------

    def clear(self) -> None:

        removed = len(self._queue)

        self._queue.clear()

        self._metrics.current_size = 0
        self._metrics.total_removed += removed

    # ----------------------------------------------------------------------

    def push(
        self,
        evidence: RawEvidence,
    ) -> BufferEntry:
        """
        Buffer one evidence object.
        """

        self._sequence += 1

        entry = BufferEntry(
            evidence=evidence,
            received_at=datetime.utcnow(),
            sequence=self._sequence,
        )

        self._queue.append(entry)

        self._metrics.current_size += 1
        self._metrics.total_received += 1

        if self._metrics.current_size > self._metrics.peak_size:
            self._metrics.peak_size = self._metrics.current_size

        return entry

    # ----------------------------------------------------------------------

    def extend(
        self,
        evidences: Iterable[RawEvidence],
    ) -> list[BufferEntry]:
        """
        Buffer many evidence objects.
        """

        entries: list[BufferEntry] = []

        for evidence in evidences:
            entries.append(self.push(evidence))

        return entries

    # ----------------------------------------------------------------------

    def peek(self) -> BufferEntry | None:
        """
        Inspect next evidence without removing it.
        """

        if not self._queue:
            return None

        return self._queue[0]

    # ----------------------------------------------------------------------

    def pop(self) -> BufferEntry | None:
        """
        Remove next evidence.
        """

        if not self._queue:
            return None

        entry = self._queue.popleft()

        self._metrics.current_size -= 1
        self._metrics.total_removed += 1

        return entry

    # ----------------------------------------------------------------------

    def pop_batch(
        self,
        batch_size: int,
    ) -> list[BufferEntry]:
        """
        Remove a synchronization batch.
        """

        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")

        batch: list[BufferEntry] = []

        while self._queue and len(batch) < batch_size:
            batch.append(self.pop())

        self._metrics.batches_processed += 1

        return batch

    # ----------------------------------------------------------------------

    def snapshot(self) -> list[BufferEntry]:
        """
        Snapshot current buffer.

        Used by replay and diagnostics.
        """

        return list(self._queue)

    # ----------------------------------------------------------------------

    def statistics(self) -> dict[str, Any]:
        """
        Export runtime statistics.
        """

        return {
            "current_size": self._metrics.current_size,
            "peak_size": self._metrics.peak_size,
            "total_received": self._metrics.total_received,
            "total_removed": self._metrics.total_removed,
            "batches_processed": self._metrics.batches_processed,
            "is_empty": self.empty,
        }

    # ----------------------------------------------------------------------

    def validate(self) -> list[str]:
        """
        Validate internal consistency.

        Returns
        -------
        List of validation issues.
        """

        issues: list[str] = []

        if self._metrics.current_size != len(self._queue):
            issues.append(
                "Buffer metric current_size does not match queue size."
            )

        if self._metrics.current_size < 0:
            issues.append(
                "Current size cannot be negative."
            )

        if self._metrics.total_removed > self._metrics.total_received:
            issues.append(
                "Removed evidence exceeds received evidence."
            )

        return issues

    # ----------------------------------------------------------------------

    def process(
        self,
        evidence: RawEvidence,
    ) -> BufferEntry:
        """
        Pipeline entry point.

        Buffer evidence and return the created buffer entry.
        """

        return self.push(evidence)