"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Desktop Trading Engine

Runtime-aware acquisition engine.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from ..base_engine import AcquisitionEngine

from .connectors import BaseConnector
from .models import DesktopEvidencePackage
from .registry import ProviderRegistry, provider_registry
from .synchronizer import (
    BatchSynchronizer,
    DesktopSynchronizer,
    SynchronizationSession,
)


# ============================================================================
# Desktop Trading Engine
# ============================================================================


class DesktopTradingEngine(AcquisitionEngine):
    """
    Runtime-aware Desktop Trading Engine.

    Owns desktop evidence acquisition while participating in the
    Evidence Acquisition Runtime lifecycle.
    """

    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
    ) -> None:

        self.registry = registry or provider_registry

        self._initialized = False
        self._running = False

        self._started_at: Optional[datetime] = None
        self._stopped_at: Optional[datetime] = None

    # =======================================================================
    # Acquisition Engine Metadata
    # =======================================================================

    @property
    def name(self) -> str:

        return "desktop_trading_engine"

    @property
    def version(self) -> str:

        return "1.0.0"

    # =======================================================================
    # Runtime Lifecycle
    # =======================================================================

    def initialize(self) -> None:
        """
        Prepare the engine.

        Heavy broker initialization is intentionally deferred until start().
        """

        self._initialized = True

    def start(self) -> None:
        """
        Start the Desktop Trading Engine.
        """

        if not self._initialized:
            self.initialize()

        self._running = True
        self._started_at = datetime.utcnow()

    def stop(self) -> None:
        """
        Stop the Desktop Trading Engine.
        """

        self._running = False
        self._stopped_at = datetime.utcnow()

    def restart(self) -> None:
        """
        Restart the engine.
        """

        self.stop()
        self.start()

    # =======================================================================
    # Runtime State
    # =======================================================================

    @property
    def is_initialized(self) -> bool:

        return self._initialized

    @property
    def is_running(self) -> bool:

        return self._running

    @property
    def is_failed(self) -> bool:

        return False

    # =======================================================================
    # Runtime Health
    # =======================================================================

    def health(self) -> Dict[str, Any]:
        """
        Return engine health.
        """

        return {
            "healthy": self._initialized,
            "running": self._running,
            "providers": len(self.registry.providers()),
        }

    # =======================================================================
    # Runtime Statistics
    # =======================================================================

    def statistics(self) -> Dict[str, Any]:
        """
        Return engine runtime statistics.
        """

        return {
            "providers": len(self.registry.providers()),
            "initialized": self._initialized,
            "running": self._running,
            "started_at": self._started_at,
            "stopped_at": self._stopped_at,
        }

    # =======================================================================
    # Provider Registry
    # =======================================================================

    @property
    def providers(self) -> List[str]:
        """
        Return registered providers.
        """

        return self.registry.providers()

    def has_provider(
        self,
        provider: str,
    ) -> bool:
        """
        Determine whether a provider is registered.
        """

        return self.registry.exists(provider)

    # =======================================================================
    # Synchronization
    # =======================================================================

    def synchronize(
        self,
        connector: BaseConnector,
    ) -> SynchronizationSession:
        """
        Execute a synchronization cycle.
        """

        synchronizer = DesktopSynchronizer(connector)

        return synchronizer.synchronize()

    def synchronize_package(
        self,
        connector: BaseConnector,
    ) -> DesktopEvidencePackage:
        """
        Synchronize and return only the evidence package.
        """

        return self.synchronize(connector).package

        # =======================================================================
    # Canonical Acquisition
    # =======================================================================

    def acquire(
        self,
        connector: BaseConnector,
    ) -> DesktopEvidencePackage:
        """
        Canonical Evidence Acquisition entry point.
        """

        return self.synchronize_package(
            connector,
        )

    # =======================================================================
    # Batch Synchronization
    # =======================================================================

    def synchronize_all(
        self,
        connectors: List[BaseConnector],
    ) -> List[SynchronizationSession]:
        """
        Synchronize multiple connectors.
        """

        synchronizer = BatchSynchronizer(connectors)

        return synchronizer.synchronize()

    def synchronize_all_packages(
        self,
        connectors: List[BaseConnector],
    ) -> List[DesktopEvidencePackage]:
        """
        Synchronize multiple connectors and return only successful
        evidence packages.
        """

        synchronizer = BatchSynchronizer(connectors)

        sessions = synchronizer.synchronize()

        return synchronizer.packages(sessions)


# ============================================================================
# Global Engine
# ============================================================================

desktop_trading_engine = DesktopTradingEngine()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "DesktopTradingEngine",
    "desktop_trading_engine",
]