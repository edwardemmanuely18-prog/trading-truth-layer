"""
Trading Truth Layer (TTL)

V2 Evidence Registry Read Service

Read-only application service for the V2 institutional
Evidence Registry.

This service does NOT:
- acquire evidence
- synchronize providers
- canonicalize evidence
- deduplicate evidence
- publish evidence
- modify registry state

It only exposes registered V2 evidence to API consumers.
"""

from __future__ import annotations

from datetime import timezone
from math import ceil
from typing import Any

from app.services.evidence_registry_v2.persistence.database import (
    database_evidence_registry_persistence,
)


def _serialize_utc_timestamp(
    value: Any,
) -> str | None:
    """
    Serialize a registry timestamp as an explicit UTC ISO-8601 value.

    The V2 registry timestamp is canonical UTC. If an older database
    driver returns a naive datetime, it is treated as UTC because the
    registry contract has always created registered_at in UTC.
    """

    if value is None:
        return None

    if value.tzinfo is None:
        value = value.replace(
            tzinfo=timezone.utc
        )
    else:
        value = value.astimezone(
            timezone.utc
        )

    return (
        value.isoformat(
            timespec="seconds"
        ).replace(
            "+00:00",
            "Z",
        )
    )


def _serialize_record(record: Any) -> dict[str, Any]:
    """
    Convert an EvidenceRegistryRecord into a stable API representation.
    """

    provider = record.provider

    metadata = dict(record.metadata or {})

    evidence_type = (
        record.evidence_type.value
        if hasattr(record.evidence_type, "value")
        else str(record.evidence_type)
    )

    return {
        "canonical_evidence_id": record.canonical_evidence_id,
        "evidence_type": evidence_type,
        "workspace_id": record.workspace_id,
        "provider_id": record.provider_id,
        "evidence_hash": record.evidence_hash,
        "evidence_version": record.evidence_version,
        "lifecycle": (
            record.lifecycle.value
            if hasattr(record.lifecycle, "value")
            else str(record.lifecycle)
        ),
        "synchronization_batch": record.synchronization_batch,
        "synchronization_session": record.synchronization_session,
        "registered_at": _serialize_utc_timestamp(
            record.registered_at
        ),
        "registered_at_utc": _serialize_utc_timestamp(
            record.registered_at
        ),
        "registered_at_timezone": "UTC",
        "provider": {
            "provider_name": provider.provider_name,
            "provider_platform": provider.provider_platform,
            "broker_server": provider.broker_server,
            "broker_account_id": provider.broker_account_id,
            "broker_account_name": provider.broker_account_name,
            "account_state": provider.account_state,
            "account_currency": provider.account_currency,
            "original_ticket_id": provider.original_ticket_id,
            "original_deal_id": provider.original_deal_id,
            "original_order_id": provider.original_order_id,
            "original_position_id": provider.original_position_id,
            "original_execution_id": provider.original_execution_id,
        },
        "metadata": metadata,
    }


def _all_workspace_records(
    workspace_id: int,
) -> list[Any]:
    """
    Collect durable V2 registry records for a workspace.

    PostgreSQL is the authoritative long-term V2 registry.
    """

    return (
        database_evidence_registry_persistence
        .workspace_records(
            workspace_id
        )
    )


def get_v2_evidence_registry(
    workspace_id: int,
) -> list[dict[str, Any]]:
    """
    Return all V2 evidence registry records for a workspace.
    """

    records = _all_workspace_records(workspace_id)

    records.sort(
        key=lambda record: record.registered_at,
        reverse=True,
    )

    return [
        _serialize_record(record)
        for record in records
    ]


def get_v2_evidence_registry_page(
    workspace_id: int,
    *,
    page: int = 1,
    page_size: int = 50,
    evidence_type: str | None = None,
    evidence_types: list[str] | None = None,
) -> dict[str, Any]:
    """
    Return one paginated page of V2 evidence registry records.
    """

    page = max(page, 1)
    page_size = min(
        max(page_size, 1),
        100,
    )

    normalized_evidence_type = (
        evidence_type.strip().upper()
        if evidence_type
        else None
    )

    normalized_evidence_types = (
        [
            value.strip().upper()
            for value in evidence_types
            if value and value.strip()
        ]
        if evidence_types
        else None
    )

    total_records = (
        database_evidence_registry_persistence
        .workspace_count(
            workspace_id,
            evidence_type=normalized_evidence_type,
            evidence_types=normalized_evidence_types,
        )
    )

    offset = (
        (page - 1)
        * page_size
    )

    records = (
        database_evidence_registry_persistence
        .workspace_records_page(
            workspace_id,
            offset=offset,
            limit=page_size,
            evidence_type=normalized_evidence_type,
            evidence_types=normalized_evidence_types,
        )
    )

    total_pages = (
        ceil(total_records / page_size)
        if total_records
        else 0
    )

    return {
        "workspace_id": workspace_id,
        "evidence_type": normalized_evidence_type,
        "evidence_types": normalized_evidence_types,
        "records": [
            _serialize_record(record)
            for record in records
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages,
        },
    }


def get_v2_evidence_packages_page(
    workspace_id: int,
    *,
    page: int = 1,
    page_size: int = 25,
) -> dict[str, Any]:

    page = max(page, 1)

    page_size = min(
        max(page_size, 1),
        100,
    )

    total_packages = (
        database_evidence_registry_persistence
        .workspace_package_count(
            workspace_id
        )
    )

    offset = (
        (page - 1)
        * page_size
    )

    packages = (
        database_evidence_registry_persistence
        .workspace_packages_page(
            workspace_id,
            offset=offset,
            limit=page_size,
        )
    )

    total_pages = (
        ceil(
            total_packages
            / page_size
        )
        if total_packages
        else 0
    )

    return {
        "workspace_id": workspace_id,
        "packages": packages,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_packages": total_packages,
            "total_pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages,
        },
    }


def get_v2_evidence_registry_summary(
    workspace_id: int,
) -> dict[str, Any]:
    """
    Return summary information for the V2 evidence registry.

    Aggregation is performed directly in PostgreSQL so the API does not
    materialize the entire workspace registry into Python.
    """

    summary = (
        database_evidence_registry_persistence
        .workspace_summary(
            workspace_id
        )
    )

    return {
        "workspace_id": workspace_id,
        "total_records": summary["total_records"],
        "lifecycle_counts": summary["lifecycle_counts"],
        "provider_counts": summary["provider_counts"],
        "evidence_type_counts": summary["evidence_type_counts"],
    }


def get_v2_evidence_record(
    workspace_id: int,
    canonical_evidence_id: str,
) -> dict[str, Any] | None:
    """
    Return one complete durable V2 evidence record.

    This is intentionally a direct primary-key/workspace lookup and
    does not materialize the entire workspace registry.
    """

    return (
        database_evidence_registry_persistence
        .get_detail(
            workspace_id,
            canonical_evidence_id,
        )
    )


def search_v2_evidence_registry(
    workspace_id: int,
    query: str,
) -> list[dict[str, Any]]:
    """
    Search V2 registry records using institutional identity fields
    and registry metadata.
    """

    normalized_query = query.strip().lower()

    if not normalized_query:
        return get_v2_evidence_registry(workspace_id)

    matches: list[dict[str, Any]] = []

    for record in _all_workspace_records(workspace_id):
        provider = record.provider

        searchable_values = [
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

        searchable_values.extend(
            str(value)
            for value in (record.metadata or {}).values()
            if value is not None
        )

        found = any(
            normalized_query in str(value).lower()
            for value in searchable_values
            if value is not None
        )

        if found:
            matches.append(_serialize_record(record))

    matches.sort(
        key=lambda item: item["registered_at"] or "",
        reverse=True,
    )

    return matches