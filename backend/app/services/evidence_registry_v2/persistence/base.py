"""
Trading Truth Layer (TTL)

V2 Evidence Registry Persistence Contract

Defines the canonical persistence interface for durable
V2 evidence registry records.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.services.universal_evidence_adapter.synchronization.evidence_registry import (
    EvidenceRegistryRecord,
)


@dataclass(slots=True)
class EvidenceRegistryPersistenceItem:
    record: EvidenceRegistryRecord

    canonical_payload: dict[str, Any] | None = None

    provenance_payload: dict[str, Any] | None = None

    payload_hash: str | None = None

    evidence_payload_size: int | None = None


class BaseEvidenceRegistryPersistence(ABC):
    """
    Canonical persistence contract for V2 Evidence Registry records.
    """

    @abstractmethod
    def save(
        self,
        record: EvidenceRegistryRecord,
        *,
        canonical_payload: dict[str, Any] | None = None,
        provenance_payload: dict[str, Any] | None = None,
        payload_hash: str | None = None,
        evidence_payload_size: int | None = None,
    ) -> None:
        """Persist one V2 evidence registry record."""
        raise NotImplementedError

    @abstractmethod
    def save_many(
        self,
        items: list[EvidenceRegistryPersistenceItem],
    ) -> None:
        """
        Persist multiple V2 evidence registry records
        in one logical operation.
        """
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        record: EvidenceRegistryRecord,
        *,
        canonical_payload: dict[str, Any] | None = None,
        provenance_payload: dict[str, Any] | None = None,
        payload_hash: str | None = None,
        evidence_payload_size: int | None = None,
    ) -> None:
        """Update one persisted V2 evidence registry record."""
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        canonical_evidence_id: str,
    ) -> EvidenceRegistryRecord | None:
        """Retrieve one V2 evidence registry record."""
        raise NotImplementedError

    @abstractmethod
    def exists(
        self,
        canonical_evidence_id: str,
    ) -> bool:
        """Determine whether a durable record exists."""
        raise NotImplementedError

    @abstractmethod
    def all(
        self,
    ) -> list[EvidenceRegistryRecord]:
        """Return all durable V2 evidence registry records."""
        raise NotImplementedError

    @abstractmethod
    def workspace_records(
        self,
        workspace_id: int,
    ) -> list[EvidenceRegistryRecord]:
        """Return all durable records belonging to a workspace."""
        raise NotImplementedError

    @abstractmethod
    def workspace_records_page(
        self,
        workspace_id: int,
        *,
        offset: int,
        limit: int,
        evidence_type: str | None = None,
        evidence_types: list[str] | None = None,
    ) -> list[EvidenceRegistryRecord]:
        """Return one paginated workspace slice."""
        raise NotImplementedError


    @abstractmethod
    def workspace_count(
        self,
        workspace_id: int,
        *,
        evidence_type: str | None = None,
        evidence_types: list[str] | None = None,
    ) -> int:
        """Return total durable records for a workspace."""
        raise NotImplementedError

    def workspace_package_count(
        self,
        workspace_id: int,
    ) -> int:
        """
        Return the number of synchronization batches
        represented in the workspace.
        """
        ...

    def workspace_packages_page(
        self,
        workspace_id: int,
        *,
        offset: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        """
        Return one page of synchronization-package summaries.
        """
        ...

    @abstractmethod
    def workspace_summary(
        self,
        workspace_id: int,
    ) -> dict[str, Any]:
        """
        Return aggregate summary statistics for a workspace.
        """
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        workspace_id: int,
        query: str,
    ) -> list[EvidenceRegistryRecord]:
        """Search durable V2 evidence records."""
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        canonical_evidence_id: str,
    ) -> None:
        """Delete one durable V2 evidence registry record."""
        raise NotImplementedError

    @abstractmethod
    def clear(
        self,
    ) -> None:
        """Remove all durable V2 evidence registry records."""
        raise NotImplementedError


__all__ = [
    "EvidenceRegistryPersistenceItem",
    "BaseEvidenceRegistryPersistence",
]