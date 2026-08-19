"""
Trading Truth Layer (TTL)

V2 Evidence Registry

In-memory persistence implementation.

Used for development and controlled testing.
"""

from __future__ import annotations

from datetime import datetime

from typing import Any

from app.services.universal_evidence_adapter.synchronization.evidence_registry import (
    EvidenceRegistryRecord,
)

from .base import (
    BaseEvidenceRegistryPersistence,
    EvidenceRegistryPersistenceItem,
)


class MemoryEvidenceRegistryPersistence(
    BaseEvidenceRegistryPersistence
):
    """
    In-memory implementation of the V2 persistence contract.
    """

    def __init__(self) -> None:
        self._records: dict[str, EvidenceRegistryRecord] = {}

    def save(
        self,
        record: EvidenceRegistryRecord,
        *,
        canonical_payload: dict[str, Any] | None = None,
        provenance_payload: dict[str, Any] | None = None,
        payload_hash: str | None = None,
        evidence_payload_size: int | None = None,
    ) -> None:
        self._records[
            record.canonical_evidence_id
        ] = record

    def save_many(
        self,
        items: list[EvidenceRegistryPersistenceItem],
    ) -> None:

        for item in items:
            self._records[
                item.record.canonical_evidence_id
            ] = item.record

    def update(
        self,
        record: EvidenceRegistryRecord,
        *,
        canonical_payload: dict[str, Any] | None = None,
        provenance_payload: dict[str, Any] | None = None,
        payload_hash: str | None = None,
        evidence_payload_size: int | None = None,
    ) -> None:
        self._records[
            record.canonical_evidence_id
        ] = record

    def get(
        self,
        canonical_evidence_id: str,
    ) -> EvidenceRegistryRecord | None:

        return self._records.get(
            canonical_evidence_id
        )

    def exists(
        self,
        canonical_evidence_id: str,
    ) -> bool:

        return canonical_evidence_id in self._records

    def all(
        self,
    ) -> list[EvidenceRegistryRecord]:

        return list(
            self._records.values()
        )

    def workspace_records(
        self,
        workspace_id: int,
    ) -> list[EvidenceRegistryRecord]:

        return [
            record
            for record in self._records.values()
            if record.workspace_id == workspace_id
        ]

    def workspace_records_page(
        self,
        workspace_id: int,
        *,
        offset: int,
        limit: int,
        evidence_type: str | None = None,
        evidence_types: list[str] | None = None,
    ) -> list[EvidenceRegistryRecord]:

        records = self.workspace_records(
            workspace_id
        )

        if evidence_types:
            records = [
                record
                for record in records
                if (
                    record.evidence_type.value
                    if hasattr(
                        record.evidence_type,
                        "value",
                    )
                    else str(record.evidence_type)
                ) in evidence_types
            ]

        elif evidence_type:
            records = [
                record
                for record in records
                if (
                    record.evidence_type.value
                    if hasattr(
                        record.evidence_type,
                        "value",
                    )
                    else str(record.evidence_type)
                ) == evidence_type
            ]

        return records[
            offset: offset + limit
        ]

    def workspace_count(
        self,
        workspace_id: int,
        *,
        evidence_type: str | None = None,
        evidence_types: list[str] | None = None,
    ) -> int:

        records = [
            record
            for record in self._records.values()
            if record.workspace_id == workspace_id
        ]

        if evidence_types:
            return sum(
                1
                for record in records
                if (
                    record.evidence_type.value
                    if hasattr(
                        record.evidence_type,
                        "value",
                    )
                    else str(record.evidence_type)
                ) in evidence_types
            )

        if evidence_type:
            return sum(
                1
                for record in records
                if (
                    record.evidence_type.value
                    if hasattr(
                        record.evidence_type,
                        "value",
                    )
                    else str(record.evidence_type)
                ) == evidence_type
            )

        return len(records)

    def workspace_package_count(
        self,
        workspace_id: int,
    ) -> int:

        batches = {
            record.synchronization_batch
            for record in self._records.values()
            if (
                record.workspace_id == workspace_id
                and record.synchronization_batch
            )
        }

        return len(batches)

    def workspace_packages_page(
        self,
        workspace_id: int,
        *,
        offset: int,
        limit: int,
    ) -> list[dict[str, Any]]:

        grouped: dict[str, list[EvidenceRegistryRecord]] = {}

        for record in self._records.values():
            if (
                record.workspace_id != workspace_id
                or not record.synchronization_batch
            ):
                continue

            grouped.setdefault(
                record.synchronization_batch,
                [],
            ).append(record)

        packages: list[dict[str, Any]] = []

        for batch, records in grouped.items():
            records.sort(
                key=lambda record: record.registered_at
                or datetime.min,
            )

            first = records[0]
            last = records[-1]

            packages.append(
                {
                    "synchronization_batch": batch,
                    "record_count": len(records),
                    "synchronization_session": (
                        first.synchronization_session
                    ),
                    "provider_name": (
                        first.provider.provider_name
                    ),
                    "provider_platform": (
                        first.provider.provider_platform
                    ),
                    "broker_account_id": (
                        first.provider.broker_account_id
                    ),
                    "first_registered_at": (
                        first.registered_at
                    ),
                    "last_registered_at": (
                        last.registered_at
                    ),
                }
            )

        packages.sort(
            key=lambda item:
                item["last_registered_at"]
                or datetime.min,
            reverse=True,
        )

        return packages[
            offset: offset + limit
        ]

    def workspace_summary(
        self,
        workspace_id: int,
    ) -> dict[str, Any]:

        records = self.workspace_records(
            workspace_id
        )

        lifecycle_counts: dict[str, int] = {}
        provider_counts: dict[str, int] = {}
        evidence_type_counts: dict[str, int] = {}

        for record in records:
            lifecycle = (
                record.lifecycle.value
                if hasattr(record.lifecycle, "value")
                else str(record.lifecycle)
            )

            lifecycle_counts[lifecycle] = (
                lifecycle_counts.get(lifecycle, 0) + 1
            )

            provider_name = record.provider.provider_name

            provider_counts[provider_name] = (
                provider_counts.get(provider_name, 0) + 1
            )

            evidence_type = (
                record.evidence_type.value
                if hasattr(record.evidence_type, "value")
                else str(record.evidence_type)
            )

            evidence_type_counts[evidence_type] = (
                evidence_type_counts.get(evidence_type, 0) + 1
            )

        return {
            "total_records": len(records),
            "lifecycle_counts": lifecycle_counts,
            "provider_counts": provider_counts,
            "evidence_type_counts": evidence_type_counts,
        }

    def search(
        self,
        workspace_id: int,
        query: str,
    ) -> list[EvidenceRegistryRecord]:

        normalized = query.strip().lower()

        records = self.workspace_records(
            workspace_id
        )

        if not normalized:
            return records

        matches: list[
            EvidenceRegistryRecord
        ] = []

        for record in records:
            provider = record.provider

            values = [
                record.canonical_evidence_id,
                record.evidence_type.value
                if hasattr(record.evidence_type, "value")
                else str(record.evidence_type),
                record.evidence_hash,
                record.provider_id,
                record.synchronization_batch,
                record.synchronization_session,
                provider.provider_name,
                provider.provider_platform,
                provider.broker_server,
                provider.broker_account_id,
                provider.broker_account_name,
                provider.account_state,
                provider.account_currency,
                provider.original_ticket_id,
                provider.original_deal_id,
                provider.original_order_id,
                provider.original_position_id,
                provider.original_execution_id,
            ]

            if any(
                normalized in str(value).lower()
                for value in values
                if value is not None
            ):
                matches.append(record)

        return matches

    def delete(
        self,
        canonical_evidence_id: str,
    ) -> None:

        self._records.pop(
            canonical_evidence_id,
            None
        )

    def clear(
        self,
    ) -> None:

        self._records.clear()


memory_evidence_registry_persistence = (
    MemoryEvidenceRegistryPersistence()
)


__all__ = [
    "MemoryEvidenceRegistryPersistence",
    "memory_evidence_registry_persistence",
]