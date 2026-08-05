"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Canonical Registry

Institutional registry for canonical Financial Engine evidence.

The registry is responsible only for storing and indexing canonical
financial evidence. It does not perform validation, translation,
verification or synchronization.
"""

from __future__ import annotations

from collections import defaultdict

from dataclasses import dataclass

from typing import DefaultDict
from typing import Dict
from typing import List
from typing import Optional

from .models import (
    CanonicalFinancialEvidence,
    FinancialSynchronizationBatch,
)


# ============================================================================
# Registry Statistics
# ============================================================================


@dataclass(slots=True)
class RegistryStatistics:
    """
    Runtime statistics for the Financial Registry.
    """

    evidence_count: int

    provider_count: int

    batch_count: int


# ============================================================================
# Financial Registry
# ============================================================================


class FinancialRegistry:
    """
    Canonical registry of Financial Engine evidence.
    """

    def __init__(self) -> None:

        self._evidence: Dict[
            str,
            CanonicalFinancialEvidence,
        ] = {}

        self._provider_index: DefaultDict[
            str,
            List[str],
        ] = defaultdict(list)

        self._batch_index: Dict[
            str,
            FinancialSynchronizationBatch,
        ] = {}

    # ---------------------------------------------------------------------
    # Registration
    # ---------------------------------------------------------------------

    def register(
        self,
        evidence: CanonicalFinancialEvidence,
    ) -> None:

        evidence_id = (
            evidence.registry.evidence_id
        )

        self._evidence[
            evidence_id
        ] = evidence

        provider = (
            evidence.evidence.provider.value
        )

        self._provider_index[
            provider
        ].append(evidence_id)

    def register_batch(
        self,
        batch: FinancialSynchronizationBatch,
    ) -> None:

        self._batch_index[
            batch.batch_id
        ] = batch

        for evidence in batch.evidences:

            self.register(evidence)

    # ---------------------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------------------

    def get(
        self,
        evidence_id: str,
    ) -> Optional[
        CanonicalFinancialEvidence
    ]:

        return self._evidence.get(
            evidence_id
        )

    def exists(
        self,
        evidence_id: str,
    ) -> bool:

        return (
            evidence_id
            in self._evidence
        )

    def by_provider(
        self,
        provider: str,
    ) -> List[
        CanonicalFinancialEvidence
    ]:

        ids = self._provider_index.get(
            provider,
            [],
        )

        return [
            self._evidence[id_]
            for id_ in ids
        ]

    def batch(
        self,
        batch_id: str,
    ) -> Optional[
        FinancialSynchronizationBatch
    ]:

        return self._batch_index.get(
            batch_id
        )

    # ---------------------------------------------------------------------
    # Listing
    # ---------------------------------------------------------------------

    def all(
        self,
    ) -> List[
        CanonicalFinancialEvidence
    ]:

        return list(
            self._evidence.values()
        )

    def providers(
        self,
    ) -> List[str]:

        return sorted(
            self._provider_index.keys()
        )

    def batches(
        self,
    ) -> List[
        FinancialSynchronizationBatch
    ]:

        return list(
            self._batch_index.values()
        )

    # ---------------------------------------------------------------------
    # Removal
    # ---------------------------------------------------------------------

    def remove(
        self,
        evidence_id: str,
    ) -> bool:

        evidence = self._evidence.pop(
            evidence_id,
            None,
        )

        if evidence is None:

            return False

        provider = (
            evidence.evidence.provider.value
        )

        if (
            provider
            in self._provider_index
        ):

            ids = self._provider_index[
                provider
            ]

            if evidence_id in ids:

                ids.remove(
                    evidence_id
                )

                if not ids:

                    del self._provider_index[
                        provider
                    ]

        return True

    def clear(self) -> None:

        self._evidence.clear()

        self._provider_index.clear()

        self._batch_index.clear()

    # ---------------------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------------------

    def statistics(
        self,
    ) -> RegistryStatistics:

        return RegistryStatistics(

            evidence_count=len(
                self._evidence
            ),

            provider_count=len(
                self._provider_index
            ),

            batch_count=len(
                self._batch_index
            ),
        )


# ============================================================================
# Registry Service
# ============================================================================


class FinancialRegistryService:
    """
    Canonical entry point for registry operations.
    """

    def __init__(
        self,
        registry: Optional[
            FinancialRegistry
        ] = None,
    ) -> None:

        self.registry = (
            registry
            or FinancialRegistry()
        )

    def register(
        self,
        evidence: CanonicalFinancialEvidence,
    ) -> None:

        self.registry.register(
            evidence
        )

    def register_batch(
        self,
        batch: FinancialSynchronizationBatch,
    ) -> None:

        self.registry.register_batch(
            batch
        )

    def lookup(
        self,
        evidence_id: str,
    ) -> Optional[
        CanonicalFinancialEvidence
    ]:

        return self.registry.get(
            evidence_id
        )

    def exists(
        self,
        evidence_id: str,
    ) -> bool:

        return self.registry.exists(
            evidence_id
        )

    def by_provider(
        self,
        provider: str,
    ) -> List[
        CanonicalFinancialEvidence
    ]:

        return self.registry.by_provider(
            provider
        )

    def statistics(
        self,
    ) -> RegistryStatistics:

        return self.registry.statistics()

    def clear(self) -> None:

        self.registry.clear()


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [
    "RegistryStatistics",
    "FinancialRegistry",
    "FinancialRegistryService",
]