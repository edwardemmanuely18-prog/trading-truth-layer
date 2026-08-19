"""
Canonical Evidence Registry

In-memory domain registry for canonical evidence.

Persistence is deliberately separated from the canonical domain model.
"""

from __future__ import annotations

from typing import Iterable

from .evidence import CanonicalEvidence


class EvidenceRegistry:
    """
    Canonical registry abstraction.

    This is the domain-level registry contract. Database persistence
    will be introduced separately.
    """

    def __init__(self) -> None:
        self._records: dict[str, CanonicalEvidence] = {}

    def register(
        self,
        evidence: CanonicalEvidence,
    ) -> CanonicalEvidence:

        evidence_id = evidence.identity.evidence_id

        if evidence_id in self._records:
            raise ValueError(
                f"Evidence '{evidence_id}' is already registered."
            )

        self._records[evidence_id] = evidence

        return evidence

    def get(
        self,
        evidence_id: str,
    ) -> CanonicalEvidence | None:
        return self._records.get(evidence_id)

    def exists(
        self,
        evidence_id: str,
    ) -> bool:
        return evidence_id in self._records

    def all(self) -> list[CanonicalEvidence]:
        return list(self._records.values())

    def by_workspace(
        self,
        workspace_id: int,
    ) -> list[CanonicalEvidence]:

        return [
            evidence
            for evidence in self._records.values()
            if evidence.identity.workspace_id == workspace_id
        ]

    def by_type(
        self,
        evidence_type: str,
    ) -> list[CanonicalEvidence]:

        return [
            evidence
            for evidence in self._records.values()
            if evidence.identity.evidence_type.value == evidence_type
        ]

    def count(self) -> int:
        return len(self._records)