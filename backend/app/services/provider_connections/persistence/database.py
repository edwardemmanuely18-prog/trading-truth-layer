"""
Trading Truth Layer (TTL)

Provider Connections

Database Persistence

SQLAlchemy-backed implementation of the canonical
Provider Connection persistence contract.

This adapter translates between:

    ProviderConnection
        <-->
    ProviderConnectionModel

The Provider Connections Service remains dependent on
BaseConnectionPersistence rather than SQLAlchemy directly.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.provider_connection import ProviderConnectionModel

from ..models import (
    ConnectionEnvironment,
    ConnectionHealth,
    ConnectionStatus,
    ConnectionStatistics,
    ProviderConnection,
)

from .base import BaseConnectionPersistence


# ============================================================
# Database Persistence
# ============================================================


class DatabaseConnectionPersistence(BaseConnectionPersistence):
    """
    PostgreSQL-backed Provider Connection persistence.

    A fresh SQLAlchemy session is created for each operation.

    This is intentionally independent from the API request
    session because Provider Connections are an application-
    level persistence concern.
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
        """
        Create a new database session.
        """

        return self.session_factory()

    # ========================================================
    # Domain -> Database
    # ========================================================

    @staticmethod
    def _to_model(
        connection: ProviderConnection,
    ) -> ProviderConnectionModel:
        """
        Convert the domain ProviderConnection into its
        SQLAlchemy persistence representation.
        """

        statistics = connection.statistics

        return ProviderConnectionModel(
            id=connection.id,
            workspace_id=connection.workspace_id,
            connection_name=connection.connection_name,
            provider=connection.provider,
            engine=connection.engine,
            environment=connection.environment.value,
            configuration=dict(
                connection.configuration,
            ),
            status=connection.status.value,
            health=connection.health.value,
            verified=connection.verified,
            connected=connection.connected,
            statistics={
                "synchronization_count": (
                    statistics.synchronization_count
                ),
                "successful_synchronizations": (
                    statistics.successful_synchronizations
                ),
                "failed_synchronizations": (
                    statistics.failed_synchronizations
                ),
                "evidence_packages": (
                    statistics.evidence_packages
                ),
                "last_synchronization": (
                    statistics.last_synchronization.isoformat()
                    if statistics.last_synchronization
                    else None
                ),
            },
            created_at=connection.created_at,
            updated_at=connection.updated_at,
        )

    # ========================================================
    # Database -> Domain
    # ========================================================

    @staticmethod
    def _to_domain(
        record: ProviderConnectionModel,
    ) -> ProviderConnection:
        """
        Convert a SQLAlchemy persistence record back into
        the canonical ProviderConnection domain model.
        """

        raw_statistics = (
            record.statistics
            if isinstance(record.statistics, dict)
            else {}
        )

        last_synchronization = (
            raw_statistics.get(
                "last_synchronization",
            )
        )

        if last_synchronization:
            if isinstance(
                last_synchronization,
                datetime,
            ):
                parsed_last_synchronization = (
                    last_synchronization
                )
            else:
                parsed_last_synchronization = (
                    datetime.fromisoformat(
                        last_synchronization,
                    )
                )
        else:
            parsed_last_synchronization = None

        statistics = ConnectionStatistics(
            synchronization_count=int(
                raw_statistics.get(
                    "synchronization_count",
                    0,
                )
            ),
            successful_synchronizations=int(
                raw_statistics.get(
                    "successful_synchronizations",
                    0,
                )
            ),
            failed_synchronizations=int(
                raw_statistics.get(
                    "failed_synchronizations",
                    0,
                )
            ),
            evidence_packages=int(
                raw_statistics.get(
                    "evidence_packages",
                    0,
                )
            ),
            last_synchronization=(
                parsed_last_synchronization
            ),
        )

        return ProviderConnection(
            id=record.id,
            workspace_id=record.workspace_id,
            connection_name=record.connection_name,
            provider=record.provider,
            engine=record.engine,
            environment=ConnectionEnvironment(
                record.environment,
            ),
            configuration=dict(
                record.configuration
                if isinstance(
                    record.configuration,
                    dict,
                )
                else {}
            ),
            status=ConnectionStatus(
                record.status,
            ),
            health=ConnectionHealth(
                record.health,
            ),
            verified=bool(
                record.verified,
            ),
            connected=bool(
                record.connected,
            ),
            created_at=record.created_at,
            updated_at=record.updated_at,
            statistics=statistics,
        )

    # ========================================================
    # CRUD
    # ========================================================

    def save(
        self,
        connection: ProviderConnection,
    ) -> None:
        """
        Persist a new Provider Connection.
        """

        db = self._session()

        try:
            existing = (
                db.query(
                    ProviderConnectionModel,
                )
                .filter(
                    ProviderConnectionModel.id
                    == connection.id,
                )
                .first()
            )

            if existing is not None:
                raise ValueError(
                    f"Provider Connection "
                    f"'{connection.id}' already exists."
                )

            db.add(
                self._to_model(
                    connection,
                )
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def update(
        self,
        connection: ProviderConnection,
    ) -> None:
        """
        Update an existing Provider Connection.
        """

        db = self._session()

        try:
            record = (
                db.query(
                    ProviderConnectionModel,
                )
                .filter(
                    ProviderConnectionModel.id
                    == connection.id,
                )
                .first()
            )

            if record is None:
                raise KeyError(
                    f"Provider Connection "
                    f"'{connection.id}' does not exist."
                )

            record.workspace_id = (
                connection.workspace_id
            )

            record.connection_name = (
                connection.connection_name
            )

            record.provider = (
                connection.provider
            )

            record.engine = (
                connection.engine
            )

            record.environment = (
                connection.environment.value
            )

            record.configuration = dict(
                connection.configuration,
            )

            record.status = (
                connection.status.value
            )

            record.health = (
                connection.health.value
            )

            record.verified = (
                connection.verified
            )

            record.connected = (
                connection.connected
            )

            statistics = connection.statistics

            record.statistics = {
                "synchronization_count": (
                    statistics.synchronization_count
                ),
                "successful_synchronizations": (
                    statistics.successful_synchronizations
                ),
                "failed_synchronizations": (
                    statistics.failed_synchronizations
                ),
                "evidence_packages": (
                    statistics.evidence_packages
                ),
                "last_synchronization": (
                    statistics.last_synchronization.isoformat()
                    if statistics.last_synchronization
                    else None
                ),
            }

            record.updated_at = (
                connection.updated_at
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def delete(
        self,
        connection_id: str,
    ) -> None:
        """
        Remove a Provider Connection.
        """

        db = self._session()

        try:
            record = (
                db.query(
                    ProviderConnectionModel,
                )
                .filter(
                    ProviderConnectionModel.id
                    == connection_id,
                )
                .first()
            )

            if record is not None:
                db.delete(record)
                db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    # ========================================================
    # Lookup
    # ========================================================

    def get(
        self,
        connection_id: str,
    ) -> Optional[ProviderConnection]:
        """
        Retrieve one Provider Connection.
        """

        db = self._session()

        try:
            record = (
                db.query(
                    ProviderConnectionModel,
                )
                .filter(
                    ProviderConnectionModel.id
                    == connection_id,
                )
                .first()
            )

            if record is None:
                return None

            return self._to_domain(
                record,
            )

        finally:
            db.close()

    def exists(
        self,
        connection_id: str,
    ) -> bool:
        """
        Determine whether a Provider Connection exists.
        """

        db = self._session()

        try:
            return (
                db.query(
                    ProviderConnectionModel.id,
                )
                .filter(
                    ProviderConnectionModel.id
                    == connection_id,
                )
                .first()
                is not None
            )

        finally:
            db.close()

    # ========================================================
    # Queries
    # ========================================================

    def all(
        self,
    ) -> List[ProviderConnection]:
        """
        Return every persisted Provider Connection.
        """

        db = self._session()

        try:
            records = (
                db.query(
                    ProviderConnectionModel,
                )
                .order_by(
                    ProviderConnectionModel.created_at.asc(),
                )
                .all()
            )

            return [
                self._to_domain(record)
                for record in records
            ]

        finally:
            db.close()

    def workspace_connections(
        self,
        workspace_id: int,
    ) -> List[ProviderConnection]:
        """
        Return all Provider Connections belonging to
        a workspace.
        """

        db = self._session()

        try:
            records = (
                db.query(
                    ProviderConnectionModel,
                )
                .filter(
                    ProviderConnectionModel.workspace_id
                    == workspace_id,
                )
                .order_by(
                    ProviderConnectionModel.created_at.asc(),
                )
                .all()
            )

            return [
                self._to_domain(record)
                for record in records
            ]

        finally:
            db.close()

    # ========================================================
    # Utilities
    # ========================================================

    def clear(
        self,
    ) -> None:
        """
        Remove every persisted Provider Connection.

        Intended primarily for controlled development/testing.
        """

        db = self._session()

        try:
            db.query(
                ProviderConnectionModel,
            ).delete(
                synchronize_session=False,
            )

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()


# ============================================================
# Global Persistence
# ============================================================

database_connection_persistence = (
    DatabaseConnectionPersistence()
)


# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "DatabaseConnectionPersistence",
    "database_connection_persistence",
]