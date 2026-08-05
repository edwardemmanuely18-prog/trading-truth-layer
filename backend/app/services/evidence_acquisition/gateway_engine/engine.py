"""
Trading Truth Layer (TTL)

Gateway Engine

Institutional orchestration layer responsible for coordinating
Gateway providers and exposing a unified synchronization API.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Any

from ..base_engine import AcquisitionEngine

from .models import GatewayEvidencePackage
from .provider import BaseGatewayProvider
from .registry import (
    GatewayProviderRegistry,
    create_provider_registry,
)

from .normalizer import (
    create_normalization_manager,
)

from .translators import (
    create_translation_manager,
)

from .synchronizer import (
    GatewaySynchronizer,
)


# ============================================================================
# Engine State
# ============================================================================


class EngineState(str, Enum):
    """
    Runtime Gateway Engine state.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    RUNNING = "running"

    STOPPED = "stopped"

    FAILED = "failed"


# ============================================================================
# Gateway Engine
# ============================================================================


class GatewayEngine(AcquisitionEngine):
    """
    Institutional orchestration engine.

    Coordinates every registered Gateway provider while exposing
    a single API to the Desktop Trading Engine.
    """

    def __init__(
        self,
        registry: Optional[
            GatewayProviderRegistry
        ] = None,
    ) -> None:

        self.registry = (
            registry
            or create_provider_registry()
        )

        self.providers: Dict[
            str,
            BaseGatewayProvider
        ] = {}

        # ---------------------------------------------------------
        # Canonical Acquisition Pipeline
        # ---------------------------------------------------------

        self.normalization_manager = (
            create_normalization_manager()
        )

        self.translator_manager = (
            create_translation_manager()
        )

        self.synchronizer = (
            GatewaySynchronizer()
        )

        self.state = EngineState.CREATED

        self.created_at = datetime.utcnow()


# ============================================================================
# Registration
# ============================================================================


    def register_provider(
        self,
        provider: BaseGatewayProvider,
    ) -> None:
        """
        Register a provider instance.
        """

        self.providers[
            provider.provider_name
        ] = provider

        self.registry.register(
            provider.descriptor,
            provider,
        )


    def unregister_provider(
        self,
        provider_name: str,
    ) -> None:
        """
        Remove a provider.
        """

        self.providers.pop(
            provider_name,
            None,
        )

        self.registry.unregister(
            provider_name,
        )


# ============================================================================
# Discovery
# ============================================================================


    def provider(
        self,
        provider_name: str,
    ) -> BaseGatewayProvider:

        return self.providers[
            provider_name
        ]


    def provider_names(
        self,
    ) -> List[str]:

        return sorted(
            self.providers.keys()
        )


    def provider_count(
        self,
    ) -> int:

        return len(
            self.providers
        )


# ============================================================================
# Lifecycle
# ============================================================================

    def initialize(self) -> None:
        """
        Initialize every registered provider.
        """

        try:

            for provider in self.providers.values():

                provider.initialize()

            self.state = EngineState.INITIALIZED

        except Exception:

            self.state = EngineState.FAILED

            raise


    def start(self) -> None:
        """
        Start every registered provider.
        """

        try:

            for provider in self.providers.values():

                provider.start()

            self.state = EngineState.RUNNING

        except Exception:

            self.state = EngineState.FAILED

            raise


    def stop(self) -> None:
        """
        Stop every registered provider.
        """

        for provider in self.providers.values():

            provider.stop()

        self.state = EngineState.STOPPED

    
    def restart(self) -> None:
        """
        Restart every registered provider.
        """

        self.stop()

        self.start()


    def close(self) -> None:
        """
        Close every registered provider.
        """

        for provider in self.providers.values():

            provider.close()

        self.state = EngineState.STOPPED


# ============================================================================
# Synchronization
# ============================================================================


    def synchronize_provider(
        self,
        provider_name: str,
    ) -> GatewayEvidencePackage:
        """
        Synchronize a single provider.
        """

        provider = self.provider(
            provider_name,
        )

        return self.synchronizer.synchronize(

            adapter=provider,

            normalization_manager=self.normalization_manager,

            translator_manager=self.translator_manager,

        )


    def synchronize_all(
        self,
    ) -> Dict[str, GatewayEvidencePackage]:
        """
        Synchronize every registered provider.

        Returns
        -------
        dict

            provider_name -> GatewayEvidencePackage
        """

        packages: Dict[
            str,
            GatewayEvidencePackage,
        ] = {}

        for provider_name, provider in (
            self.providers.items()
        ):

            packages[
                provider_name
            ] = self.synchronizer.synchronize(

                adapter=provider,

                normalization_manager=self.normalization_manager,

                translator_manager=self.translator_manager,

            )

        return packages


# ============================================================================
# Discovery
# ============================================================================


    def providers_by_gateway(
        self,
        gateway_type,
    ) -> List[BaseGatewayProvider]:
        """
        Return providers matching a gateway type.
        """

        return [

            provider

            for provider in self.providers.values()

            if provider.gateway_type == gateway_type

        ]


# ============================================================================
# State
# ============================================================================
    # ------------------------------------------------------------------
    # Engine Identity
    # ------------------------------------------------------------------

    def name(
        self,
    ) -> str:
        """
        Canonical engine name.
        """

        return "gateway_engine"


    def version(
        self,
    ) -> str:
        """
        Canonical engine version.
        """

        return "1.0"

    @property
    def is_running(self) -> bool:

        return self.state == EngineState.RUNNING


    @property
    def is_initialized(self) -> bool:

        return self.state == EngineState.INITIALIZED

    # ------------------------------------------------------------------
    # Canonical Acquisition
    # ------------------------------------------------------------------

    def acquire(
        self,
        provider_name: str,
    ) -> Any:
        """
        Canonical Evidence Acquisition entry point.
        """

        return self.synchronize_provider(
            provider_name,
        )


# ============================================================================
# Runtime Statistics
# ============================================================================

    @property
    def uptime(self):
        """
        Engine uptime.
        """

        return datetime.utcnow() - self.created_at


    def statistics(self) -> dict:
        """
        Runtime engine statistics.
        """

        return {

            "created_at": self.created_at,

            "uptime_seconds": self.uptime.total_seconds(),

            "state": self.state.value,

            "provider_count": self.provider_count(),
        }


# ============================================================================
# Health
# ============================================================================

    def health(self) -> dict:
        """
        Aggregate engine health.
        """

        return {

            "engine": {

                "state": self.state.value,

                "provider_count": self.provider_count(),

                "uptime_seconds": self.uptime.total_seconds(),
            },

            "providers": {

                provider_name: provider.health()

                for provider_name, provider in self.providers.items()

            },
        }


# ============================================================================
# Capabilities
# ============================================================================

    def capabilities(self) -> dict:
        """
        Aggregate provider capabilities.
        """

        return {

            provider_name: provider.capabilities()

            for provider_name, provider in self.providers.items()

        }


# ============================================================================
# Diagnostics
# ============================================================================

    def diagnostics(self) -> dict:
        """
        Complete engine diagnostics.
        """

        return {

            "engine": self.statistics(),

            "health": self.health(),

            "pipeline": {

                "normalizers":

                    self.normalization_manager.__class__.__name__,

                "translators":

                    self.translator_manager.__class__.__name__,

                "synchronizer":

                    self.synchronizer.__class__.__name__,

            },

            "providers": {

                provider_name:

                    provider.diagnostics()

                for provider_name, provider in self.providers.items()

            },

        }


# ============================================================================
# Representation
# ============================================================================

    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"providers={self.provider_count()}, "

            f"state={self.state.value!r})"

        )


# ============================================================================
# Shutdown
# ============================================================================

    def shutdown(self) -> None:
        """
        Gracefully shut down the Gateway Engine.

        Disconnects every registered provider and releases resources.
        """

        for provider in self.providers.values():

            try:

                provider.disconnect()

            except Exception:

                pass

            try:

                provider.close()

            except Exception:

                pass

        self.providers.clear()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [

    "EngineState",

    "GatewayEngine",
]