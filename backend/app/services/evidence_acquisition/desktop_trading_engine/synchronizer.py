"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Synchronization Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from .connectors import BaseConnector
from .exceptions import SynchronizationError
from .models import DesktopEvidencePackage
from .validators import validate_package


# ============================================================================
# Synchronization Session
# ============================================================================


@dataclass(slots=True)
class SynchronizationSession:
    """
    Represents a single synchronization cycle.

    A session provides identity, timing, and lifecycle
    information for one acquisition operation.
    """

    session_id: str

    provider: str

    started_at: datetime

    completed_at: datetime | None = None

    successful: bool = False

    package: DesktopEvidencePackage | None = None

    error: Exception | None = None

    @classmethod
    def create(
        cls,
        provider: str,
    ) -> "SynchronizationSession":
        """
        Create a new synchronization session.
        """

        return cls(
            session_id=str(uuid4()),
            provider=provider,
            started_at=datetime.utcnow(),
        )

    def complete(
        self,
        package: DesktopEvidencePackage,
    ) -> None:
        """
        Mark the synchronization as completed.
        """

        self.package = package

        self.completed_at = datetime.utcnow()

        self.successful = True

    def fail(
        self,
        error: Exception,
    ) -> None:
        """
        Mark the synchronization as failed.
        """

        self.error = error

        self.completed_at = datetime.utcnow()

        self.successful = False


# ============================================================================
# Desktop Synchronizer
# ============================================================================


class DesktopSynchronizer:
    """
    Canonical synchronization orchestrator.

    Coordinates acquisition, translation, and validation while
    remaining provider-independent.
    """

    def __init__(
        self,
        connector: BaseConnector,
    ) -> None:
        self.connector = connector

    def synchronize(
        self,
    ) -> SynchronizationSession:
        """
        Execute a complete synchronization cycle.

        Returns a SynchronizationSession containing the
        resulting DesktopEvidencePackage.
        """

        session = SynchronizationSession.create(
            provider=self.connector.provider_name,
        )

        try:
            package = self.connector.synchronize()

            validate_package(package)

            session.complete(package)

            return session

        except Exception as exc:

            import traceback

            print("=" * 80)
            print("ORIGINAL EXCEPTION")
            traceback.print_exc()
            print("=" * 80)

            session.fail(exc)

            if isinstance(exc, SynchronizationError):
                raise

            raise SynchronizationError(
                f"Synchronization failed for provider "
                f"'{self.connector.provider_name}'.",
                cause=exc,
            ) from exc

    # ------------------------------------------------------------------
    # Convenience Helpers
    # ------------------------------------------------------------------

    def synchronize_package(
        self,
    ) -> DesktopEvidencePackage:
        """
        Synchronize and return only the evidence package.
        """

        return self.synchronize().package

    def health_check(
        self,
    ) -> bool:
        """
        Return True if the underlying connector is operational.
        """

        return self.connector.is_connected()


# ============================================================================
# Batch Synchronizer
# ============================================================================


class BatchSynchronizer:
    """
    Coordinates synchronization across multiple connectors.

    Each connector executes independently and produces its own
    SynchronizationSession.
    """

    def __init__(
        self,
        connectors: list[BaseConnector],
    ) -> None:
        self.connectors = connectors

    def synchronize(
        self,
    ) -> list[SynchronizationSession]:
        """
        Execute synchronization across all registered connectors.

        Returns a list of SynchronizationSession objects.
        """

        sessions: list[SynchronizationSession] = []

        for connector in self.connectors:
            synchronizer = DesktopSynchronizer(connector)

            session = synchronizer.synchronize()

            sessions.append(session)

        return sessions

    # ------------------------------------------------------------------
    # Convenience Helpers
    # ------------------------------------------------------------------

    def successful_sessions(
        self,
        sessions: list[SynchronizationSession],
    ) -> list[SynchronizationSession]:
        """
        Return only successful synchronization sessions.
        """

        return [
            session
            for session in sessions
            if session.successful
        ]

    def failed_sessions(
        self,
        sessions: list[SynchronizationSession],
    ) -> list[SynchronizationSession]:
        """
        Return only failed synchronization sessions.
        """

        return [
            session
            for session in sessions
            if not session.successful
        ]

    def packages(
        self,
        sessions: list[SynchronizationSession],
    ) -> list[DesktopEvidencePackage]:
        """
        Extract evidence packages from successful sessions.
        """

        return [
            session.package
            for session in sessions
            if session.successful and session.package is not None
        ]


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    # Session
    "SynchronizationSession",

    # Synchronizers
    "DesktopSynchronizer",
    "BatchSynchronizer",
]