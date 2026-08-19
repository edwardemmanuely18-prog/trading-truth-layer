"""
Evidence Acquisition Runtime

Canonical runtime for the Evidence Acquisition subsystem.

Responsibilities
----------------
- Runtime state management
- Runtime configuration
- Runtime statistics
- Engine orchestration (implemented later)
- Provider orchestration (implemented later)

Business logic intentionally lives inside the individual engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from .base_engine import AcquisitionEngine

from .provider_registry import (
    ProviderRecord,
    ProviderRegistry,
)
from .lifecycle import Lifecycle
from .startup import StartupSequence
from .shutdown import ShutdownSequence
from .health import (
    HealthMonitor,
    HealthStatus,
)
from .synchronization import SynchronizationCoordinator


# ============================================================
# Runtime State
# ============================================================


class RuntimeState(str, Enum):
    """
    Canonical runtime lifecycle.
    """

    INITIALIZING = "initializing"

    READY = "ready"

    RUNNING = "running"

    STOPPING = "stopping"

    STOPPED = "stopped"

    FAILED = "failed"


# ============================================================
# Runtime Configuration
# ============================================================


@dataclass(slots=True)
class RuntimeConfiguration:
    """
    Runtime configuration.
    """

    name: str = "Evidence Acquisition Runtime"

    version: str = "1.0.0"

    auto_certify: bool = True

    auto_start: bool = False

    enable_health_monitor: bool = True

    enable_statistics: bool = True

    metadata: Dict[str, str] = field(default_factory=dict)


# ============================================================
# Runtime Statistics
# ============================================================


@dataclass(slots=True)
class RuntimeStatistics:
    """
    Runtime operational statistics.
    """

    registered_engines: int = 0

    registered_providers: int = 0

    certified_providers: int = 0

    running_engines: int = 0

    failed_engines: int = 0

    synchronization_jobs: int = 0

    active_connections: int = 0

    total_runtime_seconds: float = 0.0


# ============================================================
# Runtime Information
# ============================================================


@dataclass(slots=True)
class RuntimeInformation:
    """
    Runtime metadata.
    """

    state: RuntimeState = RuntimeState.INITIALIZING

    started_at: Optional[datetime] = None

    stopped_at: Optional[datetime] = None

    last_health_check: Optional[datetime] = None

    last_certification: Optional[datetime] = None

    version: str = "1.0.0"


# ============================================================
# Runtime
# ============================================================


class EvidenceAcquisitionRuntime:
    """
    Canonical runtime for the Evidence Acquisition subsystem.

    Construction only.

    Lifecycle methods are implemented in Section 2.
    """

    def __init__(
        self,
        configuration: Optional[RuntimeConfiguration] = None,
    ) -> None:

        self.configuration = (
            configuration
            or RuntimeConfiguration()
        )

        self.information = RuntimeInformation()

        self.statistics = RuntimeStatistics()

        #
        # Engine registry
        #

        self._engines: Dict[str, AcquisitionEngine] = {}

        #
        # Runtime Services
        #

        self._provider_registry = ProviderRegistry()

        self._lifecycle = Lifecycle()

        self._startup = StartupSequence()

        self._shutdown = ShutdownSequence()

        self._health = HealthMonitor()

        self._synchronization = SynchronizationCoordinator()

        #
        # External Components
        #

        self._certification_engine = None

    # ============================================================
    # Engine Registration
    # ============================================================

    def register_engine(
        self,
        name: str,
        engine: AcquisitionEngine,
    ) -> None:      
        """
        Register an acquisition engine.
        """

        self._engines[name] = engine

        self.statistics.registered_engines = len(
            self._engines
        )

    def unregister_engine(
        self,
        name: str,
    ) -> None:
        """
        Remove an acquisition engine.
        """

        self._engines.pop(name, None)

        self.statistics.registered_engines = len(
            self._engines
        )

    def engine(
        self,
        name: str,
    ) -> AcquisitionEngine:
        """
        Retrieve a registered engine.
        """

        if name not in self._engines:
            raise ValueError(
                f"Engine '{name}' is not registered."
            )

        return self._engines[name]

    @property
    def engines(self) -> Dict[str, AcquisitionEngine]:
        """
        Registered acquisition engines.
        """

        return self._engines


    # ============================================================
    # Provider Registration
    # ============================================================

    def register_provider(
        self,
        name: str,
        engine: str,
        provider: object,
        *,
        certified: bool = False,
        active: bool = False,
        connected: bool = False,
        metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Register a runtime provider.

        The Runtime owns the construction of the ProviderRecord.
        Engine registries remain the owners of the provider objects.
        """

        record = ProviderRecord(

            name=name,

            engine=engine,

            provider=provider,

            certified=certified,

            active=active,

            connected=connected,

            metadata=metadata or {},

        )

        self._provider_registry.register(record)

        self.statistics.registered_providers = (

            self._provider_registry.statistics().total

        )

    def unregister_provider(
        self,
        name: str,
    ) -> None:
        """
        Remove a provider.
        """

        self._provider_registry.unregister(name)

        self.statistics.registered_providers = (
            self._provider_registry.statistics().total
        )

    def provider(
        self,
        name: str,
    ) -> object:
        """
        Retrieve a provider.
        """

        return self._provider_registry.get(name)

    @property
    def providers(self) -> Dict[str, object]:
        """
        Registered providers.
        """

        return self._provider_registry

    @property
    def lifecycle(self) -> Lifecycle:
        return self._lifecycle


    @property
    def startup(self) -> StartupSequence:
        return self._startup


    @property
    def shutdown(self) -> ShutdownSequence:
        return self._shutdown


    @property
    def health(self) -> HealthMonitor:
        return self._health


    @property
    def synchronization(self) -> SynchronizationCoordinator:
        return self._synchronization


    # ============================================================
    # Dependency Injection
    # ============================================================

    def attach_certification_engine(
        self,
        engine: object,
    ) -> None:
        """
        Attach the Certification Engine.
        """

        self._certification_engine = engine

    @property
    def certification_engine(self):
        """
        Attached Certification Engine.
        """

        return self._certification_engine

    # ============================================================
    # Provider Discovery
    # ============================================================

    def _discover_providers(self) -> None:
        """
        Discover providers exposed by every registered
        acquisition engine and populate the Runtime
        Provider Registry.

        Provider ownership remains inside the engine.
        The Runtime stores only runtime records.
        """

        #
        # Fresh discovery every initialization.
        #

        self._provider_registry.clear()

        for engine in self._engines.values():

            for provider in engine.providers:

                self.register_provider(

                    name=provider,

                    engine=engine.name,

                    provider=provider,

                )


    # ============================================================
    # Lifecycle
    # ============================================================

    def _refresh_statistics(self) -> None:
        """
        Refresh runtime operational statistics.
        """

        self.statistics.registered_engines = len(self._engines)

        self.statistics.registered_providers = (
            self._provider_registry.statistics().total
        )

        self.statistics.synchronization_jobs = len(
            self._synchronization.jobs()
        )

        self.statistics.running_engines = sum(
            1
            for engine in self._engines.values()
            if getattr(engine, "is_running", False)
        )

        self.statistics.failed_engines = sum(
            1
            for engine in self._engines.values()
            if getattr(engine, "is_failed", False)
        )

        self.statistics.active_connections = sum(
            1
            for provider in self._provider_registry.active()
            if getattr(provider, "connected", False)
        )

    def initialize(self) -> None:
        """
        Initialize the runtime.

        This prepares the runtime for execution but does not start
        acquisition or synchronization.
        """

        self._lifecycle.initializing()

        self.information.state = RuntimeState.INITIALIZING

        try:

            #
            # Startup begins
            #

            self._startup.start("lifecycle")
            self._startup.complete("lifecycle")

            #
            # Register runtime health components
            #

            self._health.register("runtime")
            self._health.register("certification")
            self._health.register("synchronization")

            for name in self._engines:
                self._health.register(name)

            #
            # Future initialization hooks
            #

            # Certification Engine
            if (
                self._certification_engine is not None
                and hasattr(self._certification_engine, "initialize")
            ):
                self._startup.start("certification")

                self._certification_engine.initialize()

                self._startup.complete("certification")

                self.information.last_certification = datetime.utcnow()

            self._startup.start("engines")

            for engine in self._engines.values():
                engine.initialize()

            self._startup.complete("engines")

            #
            # Provider Discovery
            #

            self._startup.start("providers")

            self._discover_providers()

            self._startup.complete("providers")

            self._health.update(
                "runtime",
                status=HealthStatus.HEALTHY,
                message="Runtime initialized successfully.",
            )

            self.information.last_health_check = datetime.utcnow()

            self._refresh_statistics()

            self._lifecycle.ready()

            self.information.state = RuntimeState.READY

        except Exception:

            self._health.update(
                "runtime",
                status=HealthStatus.UNHEALTHY,
                message="Runtime initialization failed.",
            )

            self.information.last_health_check = datetime.utcnow()

            self._lifecycle.failed(
                "Runtime initialization failed",
            )

            self.information.state = RuntimeState.FAILED

            raise


    def start(self) -> None:
        """
        Start the runtime.
        """

        if self.information.state == RuntimeState.RUNNING:
            return

        if self.information.state == RuntimeState.INITIALIZING:
            raise RuntimeError(
                "Runtime is still initializing."
            )

        if self.information.state == RuntimeState.STOPPING:
            raise RuntimeError(
                "Runtime is stopping."
            )

        if self.information.state == RuntimeState.FAILED:
            raise RuntimeError(
                "Runtime is in FAILED state."
            )

        if self.information.state == RuntimeState.STOPPED:
            self.initialize()

        if self.information.state != RuntimeState.READY:
            self.initialize()

        self.information.started_at = datetime.utcnow()

        self._lifecycle.starting()

        for engine in self._engines.values():
            engine.start()

        self._health.update(
            "runtime",
            status=HealthStatus.HEALTHY,
            message="Runtime running.",
        )

        self.information.last_health_check = datetime.utcnow()

        self._refresh_statistics()

        self._lifecycle.running()

        self.information.state = RuntimeState.RUNNING


    def stop(self) -> None:
        """
        Stop the runtime.
        """

        if self.information.state != RuntimeState.RUNNING:
            return

        self._lifecycle.stopping()

        self.information.state = RuntimeState.STOPPING

        self._shutdown.start("engines")

        for engine in reversed(
            list(self._engines.values())
        ):
            engine.stop()

        self._health.update(
            "runtime",
            status=HealthStatus.UNKNOWN,
            message="Runtime stopped.",
        )

        self.information.last_health_check = datetime.utcnow()

        self.information.stopped_at = datetime.utcnow()

        self._refresh_statistics()

        self._lifecycle.stopped()

        self.information.state = RuntimeState.STOPPED

        self._shutdown.complete("engines")


    def restart(self) -> None:
        """
        Restart the runtime.
        """

        self.stop()

        self.initialize()

        self.start()


__all__ = [
    "RuntimeState",
    "RuntimeConfiguration",
    "RuntimeStatistics",
    "RuntimeInformation",
    "EvidenceAcquisitionRuntime",
]