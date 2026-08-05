"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Engine

Institutional façade for the Financial Infrastructure Engine.

This engine composes all Financial Engine subsystems into a
single entry point.

Responsibilities

• Provider registration
• Connector lifecycle
• Synchronization orchestration
• Registry access
• Engine health
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Dict
from typing import List
from typing import Optional
from typing import Any

from ..base_engine import AcquisitionEngine

from .financial_connector import (
    FinancialConnectorManager,
)

from .provider import (
    FinancialProvider,
    ProviderService,
)

from .registry import (
    FinancialRegistryService,
)

from .synchronizer import (
    BatchSynchronizer,
    FinancialSynchronizer,
    SynchronizationSession,
)

from .translators import (
    TranslationService,
)

from .validators import (
    ValidationService,
)


# ============================================================================
# Engine Snapshot
# ============================================================================


@dataclass(slots=True)
class FinancialEngineSnapshot:
    """
    Runtime snapshot of the Financial Engine.
    """

    initialized: bool

    started_at: Optional[datetime]

    provider_count: int

    connector_count: int

    synchronization_ready: bool


# ============================================================================
# Financial Engine
# ============================================================================


class FinancialEngine(AcquisitionEngine):
    """
    Canonical Financial Infrastructure Engine.
    """

    def __init__(self) -> None:

        self.connector_manager = (
            FinancialConnectorManager()
        )

        self.provider_service = (
            ProviderService()
        )

        self.registry = (
            FinancialRegistryService()
        )

        self.translation_service = (
            TranslationService()
        )

        self.validation_service = (
            ValidationService()
        )

        self.synchronizer = (
            FinancialSynchronizer(
                registry=self.registry,
                translators=self.translation_service,
                validators=self.validation_service,
            )
        )

        self._initialized = False

        self._running = False

        self._started_at: Optional[
            datetime
        ] = None

        self._stopped_at: Optional[
            datetime
        ] = None


    # ------------------------------------------------------------------
    # Engine Metadata
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:

        return "financial_engine"


    @property
    def version(self) -> str:

        return "1.0.0"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """
        Prepare the Financial Engine.

        Heavy provider initialization is deferred until start().
        """

        self._initialized = True

    def start(self) -> None:
        """
        Start the Financial Engine.
        """

        if not self._initialized:

            self.initialize()

        self.connector_manager.connect_all()

        self.connector_manager.authenticate_all()

        self._running = True

        self._started_at = datetime.utcnow()

    def stop(self) -> None:
        """
        Stop the Financial Engine.
        """

        self.connector_manager.disconnect_all()

        self._running = False

        self._stopped_at = datetime.utcnow()

    def restart(self) -> None:
        """
        Restart the Financial Engine.
        """

        self.stop()

        self.start()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_provider(
        self,
        provider: FinancialProvider,
    ) -> None:

        self.provider_service.register(
            provider
        )

        self.connector_manager.register(
            provider.connector
        )

    @property
    def providers(
        self,
    ) -> list[str]:
        """
        Return registered providers.
        """

        return [

            provider.name()

            for provider in self.provider_service.providers()

        ]


    def has_provider(
        self,
        provider: str,
    ) -> bool:
        """
        Determine whether a provider is registered.
        """

        return (

            self.provider_service.provider(
                provider,
            )

            is not None

        )

    # ------------------------------------------------------------------
    # Synchronization
    # ------------------------------------------------------------------

    def synchronize(
        self,
        provider_name: str,
    ) -> SynchronizationSession:

        provider = (
            self.provider_service.provider(
                provider_name
            )
        )

        if provider is None:

            raise ValueError(
                f"Unknown provider: {provider_name}"
            )

        return self.synchronizer.synchronize(
            provider
        )

    def synchronize_package(
        self,
        provider_name: str,
    ):
        """
        Synchronize and return only the canonical batch.
        """

        provider = self.provider_service.provider(
            provider_name,
        )

        if provider is None:

            raise ValueError(
                f"Unknown provider: {provider_name}"
            )

        return self.synchronizer.synchronize_batch(
            provider,
        )

    def synchronize_all(
        self,
    ) -> list[SynchronizationSession]:
        """
        Synchronize all registered providers.
        """

        synchronizer = BatchSynchronizer(
            self.synchronizer,
        )

        return synchronizer.synchronize(

            self.provider_service.providers(),

        )

    def synchronize_all_packages(
        self,
    ):
        """
        Synchronize all providers and return only
        successfully synchronized batches.
        """

        synchronizer = BatchSynchronizer(
            self.synchronizer,
        )

        sessions = synchronizer.synchronize(

            self.provider_service.providers(),

        )

        return synchronizer.batches(
            sessions,
        )

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    @property
    def is_initialized(self) -> bool:

        return self._initialized


    @property
    def is_running(self) -> bool:

        return self._running


    @property
    def is_failed(self) -> bool:

        return False


    def health(self) -> Dict[str, Any]:
        """
        Return Financial Engine health.
        """

        return {

            "healthy": self._initialized,

            "running": self._running,

            "providers": self.provider_service.count(),

            "connectors": self.connector_manager.connector_count(),

        }

    def statistics(
        self,
    ) -> Dict[str, Any]:
        """
        Return runtime statistics.
        """

        return {

            "providers": self.provider_service.count(),

            "connectors": self.connector_manager.connector_count(),

            "initialized": self._initialized,

            "running": self._running,

            "started_at": self._started_at,

            "stopped_at": self._stopped_at,

        }

    # ------------------------------------------------------------------
    # Canonical Acquisition
    # ------------------------------------------------------------------

    def acquire(
        self,
        provider_name: str,
    ):
        """
        Canonical Financial Evidence Acquisition entry point.
        """

        return self.synchronize_package(
            provider_name,
        )

    def snapshot(
        self,
    ) -> FinancialEngineSnapshot:

        return FinancialEngineSnapshot(

            initialized=self._initialized,

            started_at=self._started_at,

            provider_count=(
                self.provider_service.count()
            ),

            connector_count=(
                self.connector_manager.connector_count()
            ),

            synchronization_ready=(
                self.connector_manager
                .synchronization_ready()
            ),
        )

    # ------------------------------------------------------------------
    # Registry
    # ------------------------------------------------------------------

    def registry_statistics(self):

        return (
            self.registry.statistics()
        )

    def clear_registry(self) -> None:

        self.registry.clear()


financial_engine = FinancialEngine()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [

    "FinancialEngineSnapshot",

    "FinancialEngine",

    "financial_engine",
]