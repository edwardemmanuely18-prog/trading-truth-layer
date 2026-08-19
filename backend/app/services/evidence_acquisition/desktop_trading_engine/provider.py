"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Desktop Evidence Provider
"""

from __future__ import annotations

from typing import Optional

from .connectors import BaseConnector
from .models import DesktopEvidencePackage
from .synchronizer import (
    DesktopSynchronizer,
    SynchronizationSession,
)
from .verification import (
    VerificationResult,
    desktop_verification_engine,
)


# ============================================================================
# Desktop Evidence Provider
# ============================================================================


class DesktopEvidenceProvider:
    """
    Canonical provider for desktop trading evidence.

    This provider is broker-independent.

    Every supported desktop trading platform is integrated
    through an adapter while this provider exposes a single,
    canonical evidence acquisition interface.
    """

    def __init__(
        self,
        connector: BaseConnector,
    ) -> None:
        self.connector = connector

        self._synchronizer = DesktopSynchronizer(
            connector,
        )

    @property
    def provider_name(self) -> str:
        """
        Return the underlying provider name.
        """

        return self.connector.provider_name

    @property
    def provider_version(self) -> str:
        """
        Return the provider version.
        """

        return self.connector.provider_version

    def acquire(
        self,
    ) -> SynchronizationSession:
        """
        Acquire desktop trading evidence.

        Returns the complete synchronization session.
        """

        return self._synchronizer.synchronize()

    def acquire_package(
        self,
    ) -> Optional[DesktopEvidencePackage]:
        """
        Acquire only the canonical evidence package.
        """

        session = self.acquire()

        return session.package


    # ------------------------------------------------------------------
    # Evidence Acquisition
    # ------------------------------------------------------------------

    def acquire_and_validate(
        self,
    ) -> DesktopEvidencePackage:
        """
        Acquire and validate a canonical desktop evidence package.

        Raises an exception if synchronization does not produce a
        valid evidence package.
        """

        package = self.acquire_package()

        if package is None:
            raise RuntimeError(
                "Desktop evidence acquisition completed without "
                "returning an evidence package."
            )

        return package

    def health_check(
        self,
    ) -> bool:
        """
        Determine whether the underlying connector is operational.
        """

        return self._synchronizer.health_check()

    def is_available(
        self,
    ) -> bool:
        """
        Determine whether the provider is available for acquisition.
        """

        return self.health_check()

    def reconnect(
        self,
    ) -> bool:
        """
        Re-establish the underlying connector if necessary.
        """

        self.connector.disconnect()

        self.connector.connect()

        return self.health_check()

    def close(
        self,
    ) -> None:
        """
        Gracefully close the underlying connector.
        """

        self.connector.disconnect()


    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """
        Establish the underlying connector.
        """

        self.connector.connect()

    def disconnect(self) -> None:
        """
        Disconnect the underlying connector.
        """

        self.connector.disconnect()

    @property
    def connected(self) -> bool:
        """
        Determine whether the connector is currently connected.
        """

        return self.connector.is_connected()

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify(
        self,
        *,
        expected_account_id: str | None = None,
        expected_server: str | None = None,
        expected_provider: str | None = None,
    ) -> VerificationResult:
        """
        Execute the canonical Desktop Verification Engine.

        Provider-specific observation remains inside the adapter.
        Verification policy remains inside DesktopVerificationEngine.
        """

        snapshot = (
            self.connector.adapter
            .get_verification_snapshot()
        )

        return desktop_verification_engine.verify(
            snapshot,
            expected_account_id=expected_account_id,
            expected_server=expected_server,
            expected_provider=expected_provider,
        )

    def __enter__(self) -> "DesktopEvidenceProvider":
        """
        Context manager entry.
        """

        self.connect()

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ) -> None:
        """
        Context manager exit.
        """

        self.disconnect()


desktop_evidence_provider = DesktopEvidenceProvider

__all__ = [
    "DesktopEvidenceProvider",
]