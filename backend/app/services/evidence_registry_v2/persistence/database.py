"""
Trading Truth Layer (TTL)

V2 Evidence Registry

SQLAlchemy-backed durable persistence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from sqlalchemy import func

from app.core.db import SessionLocal
from app.models.evidence_registry import EvidenceRegistryModel
from app.services.universal_evidence_adapter.synchronization.evidence_registry import (
    EvidenceRegistryRecord,
    ProviderIdentity,
)
from app.services.universal_evidence_adapter.synchronization.evidence_registry import (
    EvidenceLifecycle,
)

from .base import (
    BaseEvidenceRegistryPersistence,
    EvidenceRegistryPersistenceItem,
)


class DatabaseEvidenceRegistryPersistence(
    BaseEvidenceRegistryPersistence
):
    """
    PostgreSQL-backed V2 Evidence Registry persistence.

    A fresh database session is created for each operation.
    """

    def __init__(
        self,
        session_factory=SessionLocal,
    ) -> None:
        self.session_factory = session_factory

    # ========================================================
    # Session
    # ========================================================

    def _session(self) -> Session:
        return self.session_factory()

    # ========================================================
    # Serialization helpers
    # ========================================================

    @staticmethod
    def _json_safe(
        value: Any,
    ) -> Any:

        if value is None:
            return None

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, dict):
            return {
                str(key): DatabaseEvidenceRegistryPersistence._json_safe(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [
                DatabaseEvidenceRegistryPersistence._json_safe(
                    item
                )
                for item in value
            ]

        if hasattr(value, "value"):
            return value.value

        if hasattr(value, "__dict__"):
            return {
                str(key): DatabaseEvidenceRegistryPersistence._json_safe(
                    item
                )
                for key, item in vars(value).items()
            }

        return value

    @staticmethod
    def _evidence_type(
        record: EvidenceRegistryRecord,
    ) -> str:

        if hasattr(
            record.evidence_type,
            "value",
        ):
            return str(
                record.evidence_type.value
            )

        return str(
            record.evidence_type
        )

    @staticmethod
    def _lifecycle(
        record: EvidenceRegistryRecord,
    ) -> str:

        if hasattr(
            record.lifecycle,
            "value",
        ):
            return str(
                record.lifecycle.value
            )

        return str(
            record.lifecycle
        )

    # ========================================================
    # Domain -> Database
    # ========================================================

    @classmethod
    def _to_model(
        cls,
        record: EvidenceRegistryRecord,
        *,
        canonical_payload: dict[str, Any] | None = None,
        provenance_payload: dict[str, Any] | None = None,
        payload_hash: str | None = None,
        evidence_payload_size: int | None = None,
    ) -> EvidenceRegistryModel:

        provider = record.provider

        return EvidenceRegistryModel(
            canonical_evidence_id=(
                record.canonical_evidence_id
            ),
            workspace_id=record.workspace_id,
            provider_id=record.provider_id,

            evidence_type=cls._evidence_type(
                record
            ),
            evidence_hash=record.evidence_hash,
            evidence_version=record.evidence_version,
            lifecycle=cls._lifecycle(record),

            synchronization_batch=(
                record.synchronization_batch
            ),
            synchronization_session=(
                record.synchronization_session
            ),
            registered_at=record.registered_at,

            provider_name=provider.provider_name,
            provider_platform=provider.provider_platform,
            broker_server=provider.broker_server,
            broker_account_id=provider.broker_account_id,
            broker_account_name=provider.broker_account_name,
            account_state=provider.account_state,
            account_currency=provider.account_currency,

            original_ticket_id=(
                provider.original_ticket_id
            ),
            original_order_id=(
                provider.original_order_id
            ),
            original_deal_id=(
                provider.original_deal_id
            ),
            original_position_id=(
                provider.original_position_id
            ),
            original_execution_id=(
                provider.original_execution_id
            ),

            metadata_payload=(
                cls._json_safe(
                    record.metadata
                )
            ),
            canonical_payload=(
                cls._json_safe(
                    canonical_payload
                )
                if canonical_payload is not None
                else None
            ),
            provenance_payload=(
                cls._json_safe(
                    provenance_payload
                )
                if provenance_payload is not None
                else None
            ),
            payload_hash=payload_hash,
            evidence_payload_size=evidence_payload_size,
        )

    # ========================================================
    # Database -> Domain
    # ========================================================

    @staticmethod
    def _to_domain(
        model: EvidenceRegistryModel,
    ) -> EvidenceRegistryRecord:

        provider = ProviderIdentity(
            provider_name=model.provider_name,
            provider_platform=model.provider_platform,
            broker_server=model.broker_server,
            broker_account_id=model.broker_account_id,
            broker_account_name=model.broker_account_name,
            account_state=model.account_state,
            account_currency=model.account_currency,
            original_ticket_id=model.original_ticket_id,
            original_order_id=model.original_order_id,
            original_deal_id=model.original_deal_id,
            original_position_id=model.original_position_id,
            original_execution_id=model.original_execution_id,
        )

        evidence_type = model.evidence_type

        lifecycle = model.lifecycle

        try:
            evidence_type = (
                __import__(
                    "app.services.universal_evidence_adapter.domain.transport.raw_evidence",
                    fromlist=["EvidenceType"],
                ).EvidenceType(
                    evidence_type
                )
            )
        except (ValueError, TypeError):
            pass

        try:
            lifecycle = EvidenceLifecycle(
                lifecycle
            )
        except (ValueError, TypeError):
            pass

        return EvidenceRegistryRecord(
            canonical_evidence_id=(
                model.canonical_evidence_id
            ),
            provider=provider,
            workspace_id=model.workspace_id,
            provider_id=model.provider_id,
            evidence_hash=model.evidence_hash,
            evidence_type=evidence_type,
            evidence_version=model.evidence_version,
            lifecycle=lifecycle,
            synchronization_batch=(
                model.synchronization_batch
            ),
            synchronization_session=(
                model.synchronization_session
            ),
            registered_at=model.registered_at,
            metadata=dict(
                model.metadata_payload or {}
            ),
        )

    # ========================================================
    # CRUD
    # ========================================================

    def save(
        self,
        record: EvidenceRegistryRecord,
        *,
        canonical_payload: dict[str, Any] | None = None,
        provenance_payload: dict[str, Any] | None = None,
        payload_hash: str | None = None,
        evidence_payload_size: int | None = None,
    ) -> None:

        db = self._session()

        try:
            existing = (
                db.query(
                    EvidenceRegistryModel
                )
                .filter(
                    EvidenceRegistryModel.canonical_evidence_id
                    == record.canonical_evidence_id
                )
                .first()
            )

            if existing is not None:
                raise ValueError(
                    "V2 evidence registry record "
                    f"'{record.canonical_evidence_id}' "
                    "already exists."
                )

            db.add(
                self._to_model(
                    record,
                    canonical_payload=canonical_payload,
                    provenance_payload=provenance_payload,
                    payload_hash=payload_hash,
                    evidence_payload_size=evidence_payload_size,
                )
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def save_many(
        self,
        items: list[EvidenceRegistryPersistenceItem],
    ) -> None:

        if not items:
            return

        db = self._session()

        try:
            canonical_ids = [
                item.record.canonical_evidence_id
                for item in items
            ]

            existing_ids = {
                row[0]
                for row in (
                    db.query(
                        EvidenceRegistryModel.canonical_evidence_id
                    )
                    .filter(
                        EvidenceRegistryModel.canonical_evidence_id.in_(
                            canonical_ids
                        )
                    )
                    .all()
                )
            }

            models = [
                self._to_model(
                    item.record,
                    canonical_payload=item.canonical_payload,
                    provenance_payload=item.provenance_payload,
                    payload_hash=item.payload_hash,
                    evidence_payload_size=item.evidence_payload_size,
                )
                for item in items
                if item.record.canonical_evidence_id
                not in existing_ids
            ]

            if models:
                db.add_all(models)

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def update(
        self,
        record: EvidenceRegistryRecord,
        *,
        canonical_payload: dict[str, Any] | None = None,
        provenance_payload: dict[str, Any] | None = None,
        payload_hash: str | None = None,
        evidence_payload_size: int | None = None,
    ) -> None:

        db = self._session()

        try:
            model = (
                db.query(
                    EvidenceRegistryModel
                )
                .filter(
                    EvidenceRegistryModel.canonical_evidence_id
                    == record.canonical_evidence_id
                )
                .first()
            )

            if model is None:
                raise KeyError(
                    "V2 evidence registry record "
                    f"'{record.canonical_evidence_id}' "
                    "does not exist."
                )

            replacement = self._to_model(
                record,
                canonical_payload=canonical_payload,
                provenance_payload=provenance_payload,
                payload_hash=payload_hash,
                evidence_payload_size=evidence_payload_size,
            )

            for column in (
                "workspace_id",
                "provider_id",
                "evidence_type",
                "evidence_hash",
                "evidence_version",
                "lifecycle",
                "synchronization_batch",
                "synchronization_session",
                "registered_at",
                "provider_name",
                "provider_platform",
                "broker_server",
                "broker_account_id",
                "broker_account_name",
                "account_state",
                "account_currency",
                "original_ticket_id",
                "original_order_id",
                "original_deal_id",
                "original_position_id",
                "original_execution_id",
                "metadata_payload",
                "canonical_payload",
                "provenance_payload",
                "payload_hash",
                "evidence_payload_size",
            ):
                setattr(
                    model,
                    column,
                    getattr(
                        replacement,
                        column,
                    ),
                )

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def get(
        self,
        canonical_evidence_id: str,
    ) -> EvidenceRegistryRecord | None:

        db = self._session()

        try:
            model = (
                db.query(
                    EvidenceRegistryModel
                )
                .filter(
                    EvidenceRegistryModel.canonical_evidence_id
                    == canonical_evidence_id
                )
                .first()
            )

            if model is None:
                return None

            return self._to_domain(model)

        finally:
            db.close()

    def get_detail(
        self,
        workspace_id: int,
        canonical_evidence_id: str,
    ) -> dict[str, Any] | None:
        """
        Return the complete durable V2 evidence record.

        This is the detail-read contract. It intentionally returns
        the persisted canonical and provenance payloads in addition
        to registry identity fields.
        """

        db = self._session()

        try:
            model = (
                db.query(
                    EvidenceRegistryModel
                )
                .filter(
                    EvidenceRegistryModel.workspace_id
                    == workspace_id,
                    EvidenceRegistryModel.canonical_evidence_id
                    == canonical_evidence_id,
                )
                .first()
            )

            if model is None:
                return None

            return {
                "canonical_evidence_id": (
                    model.canonical_evidence_id
                ),
                "workspace_id": model.workspace_id,
                "provider_id": model.provider_id,
                "evidence_type": model.evidence_type,
                "evidence_hash": model.evidence_hash,
                "evidence_version": model.evidence_version,
                "lifecycle": model.lifecycle,

                "synchronization_batch": (
                    model.synchronization_batch
                ),
                "synchronization_session": (
                    model.synchronization_session
                ),

                "registered_at": (
                    model.registered_at.isoformat()
                    if model.registered_at is not None
                    else None
                ),

                "registered_at_utc": (
                    model.registered_at.isoformat()
                    if model.registered_at is not None
                    else None
                ),
                "registered_at_timezone": "UTC",

                "provider": {
                    "provider_name": model.provider_name,
                    "provider_platform": model.provider_platform,
                    "broker_server": model.broker_server,
                    "broker_account_id": model.broker_account_id,
                    "broker_account_name": model.broker_account_name,
                    "account_state": model.account_state,
                    "account_currency": model.account_currency,
                    "original_ticket_id": model.original_ticket_id,
                    "original_order_id": model.original_order_id,
                    "original_deal_id": model.original_deal_id,
                    "original_position_id": model.original_position_id,
                    "original_execution_id": model.original_execution_id,
                },

                "metadata": dict(
                    model.metadata_payload or {}
                ),

                "canonical_payload": (
                    model.canonical_payload
                ),

                "provenance_payload": (
                    model.provenance_payload
                ),

                "payload_hash": model.payload_hash,

                "evidence_payload_size": (
                    model.evidence_payload_size
                ),
            }

        finally:
            db.close()

    def exists(
        self,
        canonical_evidence_id: str,
    ) -> bool:

        db = self._session()

        try:
            return (
                db.query(
                    EvidenceRegistryModel.canonical_evidence_id
                )
                .filter(
                    EvidenceRegistryModel.canonical_evidence_id
                    == canonical_evidence_id
                )
                .first()
                is not None
            )

        finally:
            db.close()

    def all(
        self,
    ) -> list[EvidenceRegistryRecord]:

        db = self._session()

        try:
            models = (
                db.query(
                    EvidenceRegistryModel
                )
                .order_by(
                    EvidenceRegistryModel.registered_at.desc()
                )
                .all()
            )

            return [
                self._to_domain(model)
                for model in models
            ]

        finally:
            db.close()

    def workspace_records(
        self,
        workspace_id: int,
    ) -> list[EvidenceRegistryRecord]:

        db = self._session()

        try:
            models = (
                db.query(
                    EvidenceRegistryModel
                )
                .filter(
                    EvidenceRegistryModel.workspace_id
                    == workspace_id
                )
                .order_by(
                    EvidenceRegistryModel.registered_at.desc()
                )
                .all()
            )

            return [
                self._to_domain(model)
                for model in models
            ]

        finally:
            db.close()

    def workspace_records_page(
        self,
        workspace_id: int,
        *,
        offset: int,
        limit: int,
        evidence_type: str | None = None,
        evidence_types: list[str] | None = None,
    ) -> list[EvidenceRegistryRecord]:

        db = self._session()

        try:
            query = db.query(
                EvidenceRegistryModel
            ).filter(
                EvidenceRegistryModel.workspace_id
                == workspace_id
            )

            if evidence_types:
                query = query.filter(
                    EvidenceRegistryModel.evidence_type.in_(
                        evidence_types
                    )
                )
            elif evidence_type:
                query = query.filter(
                    EvidenceRegistryModel.evidence_type
                    == evidence_type
                )

            models = (
                query
                .order_by(
                    EvidenceRegistryModel.registered_at.desc()
                )
                .offset(offset)
                .limit(limit)
                .all()
            )

            return [
                self._to_domain(model)
                for model in models
            ]

        finally:
            db.close()

    def workspace_count(
        self,
        workspace_id: int,
        *,
        evidence_type: str | None = None,
        evidence_types: list[str] | None = None,
    ) -> int:

        db = self._session()

        try:
            query = db.query(
                EvidenceRegistryModel
            ).filter(
                EvidenceRegistryModel.workspace_id
                == workspace_id
            )

            if evidence_types:
                query = query.filter(
                    EvidenceRegistryModel.evidence_type.in_(
                        evidence_types
                    )
                )
            elif evidence_type:
                query = query.filter(
                    EvidenceRegistryModel.evidence_type
                    == evidence_type
                )

            return query.count()

        finally:
            db.close()

    def workspace_package_count(
        self,
        workspace_id: int,
    ) -> int:

        db = self._session()

        try:
            return (
                db.query(
                    EvidenceRegistryModel.synchronization_batch
                )
                .filter(
                    EvidenceRegistryModel.workspace_id
                    == workspace_id,
                    EvidenceRegistryModel.synchronization_batch
                    .isnot(None),
                )
                .distinct()
                .count()
            )

        finally:
            db.close()

    def workspace_packages_page(
        self,
        workspace_id: int,
        *,
        offset: int,
        limit: int,
    ) -> list[dict[str, Any]]:

        db = self._session()

        try:
            rows = (
                db.query(
                    EvidenceRegistryModel.synchronization_batch.label(
                        "synchronization_batch"
                    ),
                    func.count(
                        EvidenceRegistryModel.canonical_evidence_id
                    ).label(
                        "record_count"
                    ),
                    func.min(
                        EvidenceRegistryModel.synchronization_session
                    ).label(
                        "synchronization_session"
                    ),
                    func.min(
                        EvidenceRegistryModel.provider_name
                    ).label(
                        "provider_name"
                    ),
                    func.min(
                        EvidenceRegistryModel.provider_platform
                    ).label(
                        "provider_platform"
                    ),
                    func.min(
                        EvidenceRegistryModel.broker_account_id
                    ).label(
                        "broker_account_id"
                    ),
                    func.min(
                        EvidenceRegistryModel.registered_at
                    ).label(
                        "first_registered_at"
                    ),
                    func.max(
                        EvidenceRegistryModel.registered_at
                    ).label(
                        "last_registered_at"
                    ),
                )
                .filter(
                    EvidenceRegistryModel.workspace_id
                    == workspace_id,
                    EvidenceRegistryModel.synchronization_batch
                    .isnot(None),
                )
                .group_by(
                    EvidenceRegistryModel.synchronization_batch
                )
                .order_by(
                    func.max(
                        EvidenceRegistryModel.registered_at
                    ).desc()
                )
                .offset(offset)
                .limit(limit)
                .all()
            )

            return [
                {
                    "synchronization_batch": row.synchronization_batch,
                    "record_count": int(row.record_count or 0),
                    "synchronization_session": row.synchronization_session,
                    "provider_name": row.provider_name,
                    "provider_platform": row.provider_platform,
                    "broker_account_id": row.broker_account_id,
                    "first_registered_at": row.first_registered_at,
                    "last_registered_at": row.last_registered_at,
                }
                for row in rows
            ]

        finally:
            db.close()

    def workspace_summary(
        self,
        workspace_id: int,
    ) -> dict[str, Any]:
        """
        Return aggregate V2 registry statistics directly from PostgreSQL.

        This avoids materializing the complete workspace registry into
        Python just to calculate summary counts.
        """

        db = self._session()

        try:
            total_records = (
                db.query(
                    func.count(
                        EvidenceRegistryModel.canonical_evidence_id
                    )
                )
                .filter(
                    EvidenceRegistryModel.workspace_id
                    == workspace_id
                )
                .scalar()
                or 0
            )

            lifecycle_rows = (
                db.query(
                    EvidenceRegistryModel.lifecycle,
                    func.count(
                        EvidenceRegistryModel.canonical_evidence_id
                    ),
                )
                .filter(
                    EvidenceRegistryModel.workspace_id
                    == workspace_id
                )
                .group_by(
                    EvidenceRegistryModel.lifecycle
                )
                .all()
            )

            provider_rows = (
                db.query(
                    EvidenceRegistryModel.provider_name,
                    func.count(
                        EvidenceRegistryModel.canonical_evidence_id
                    ),
                )
                .filter(
                    EvidenceRegistryModel.workspace_id
                    == workspace_id
                )
                .group_by(
                    EvidenceRegistryModel.provider_name
                )
                .all()
            )

            evidence_type_rows = (
                db.query(
                    EvidenceRegistryModel.evidence_type,
                    func.count(
                        EvidenceRegistryModel.canonical_evidence_id
                    ),
                )
                .filter(
                    EvidenceRegistryModel.workspace_id
                    == workspace_id
                )
                .group_by(
                    EvidenceRegistryModel.evidence_type
                )
                .all()
            )

            return {
                "total_records": int(
                    total_records
                ),
                "lifecycle_counts": {
                    str(lifecycle): int(count)
                    for lifecycle, count
                    in lifecycle_rows
                },
                "provider_counts": {
                    str(provider): int(count)
                    for provider, count
                    in provider_rows
                },
                "evidence_type_counts": {
                    str(evidence_type): int(count)
                    for evidence_type, count
                    in evidence_type_rows
                },
            }

        finally:
            db.close()

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
                self._evidence_type(record),
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

            values.extend(
                str(value)
                for value in (
                    record.metadata or {}
                ).values()
                if value is not None
            )

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

        db = self._session()

        try:
            model = (
                db.query(
                    EvidenceRegistryModel
                )
                .filter(
                    EvidenceRegistryModel.canonical_evidence_id
                    == canonical_evidence_id
                )
                .first()
            )

            if model is not None:
                db.delete(model)
                db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def clear(
        self,
    ) -> None:

        db = self._session()

        try:
            db.query(
                EvidenceRegistryModel
            ).delete(
                synchronize_session=False
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()


database_evidence_registry_persistence = (
    DatabaseEvidenceRegistryPersistence()
)


__all__ = [
    "DatabaseEvidenceRegistryPersistence",
    "database_evidence_registry_persistence",
]