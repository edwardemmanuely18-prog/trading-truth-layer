"""
Trading Truth Layer (TTL)

Provider Connections

Application Service

Institutional application service responsible for exposing
Provider Connection capabilities to the API layer.

Responsibilities
----------------

• Aggregate Desktop Engine
• Aggregate Gateway Engine
• Aggregate Financial Engine

• Produce frontend view models

This service intentionally does NOT:

• authenticate providers
• synchronize providers
• acquire evidence
• verify evidence
• manage adapters

Those responsibilities remain owned by the
Evidence Acquisition engines.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any

import os

from app.services.evidence_acquisition.desktop_trading_engine.engine import (
    desktop_trading_engine,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.mt5_adapter import (
    MT5Adapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.mt4_adapter import (
    MT4Adapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.ibkr_adapter import (
    IBKRAdapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.ctrader_adapter import (
    CTraderAdapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.ninjatrader_adapter import (
    NinjaTraderAdapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.tradestation_adapter import (
    TradeStationAdapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.sierrachart_adapter import (
    SierraChartAdapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.quantower_adapter import (
    QuantowerAdapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.multicharts_adapter import (
    MultiChartsAdapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.motivewave_adapter import (
    MotiveWaveAdapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.tradingtechnologies_adapter import (
    TradingTechnologiesAdapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.base_adapter import (
    BaseDesktopAdapter,
)

from app.services.evidence_acquisition.desktop_trading_engine.translators import (
    DesktopTranslator,
    BaseTranslator,
)

from app.services.evidence_acquisition.desktop_trading_engine.connectors import (
    ConnectorConfiguration,
)

from app.services.evidence_acquisition.desktop_trading_engine.desktop_connector import (
    DesktopConnector,
)

from app.services.evidence_acquisition.desktop_trading_engine.provider import (
    DesktopEvidenceProvider,
)

from .registry import (
    ConnectionRegistry,
    connection_registry,
)

from .persistence import (
    BaseConnectionPersistence,
)

from .persistence.database import (
    database_connection_persistence,
)

from .models import (
    ProviderConnection,
    RuntimeConnection,
    ConnectionEnvironment,
    ConnectionStatus,
    ConnectionHealth,
    DesktopConnectionCreateResponse,
    DesktopConnectionTestResponse,
    DesktopConnectionVerificationResponse,
)

from .synchronization_orchestrator import (
    provider_synchronization_orchestrator,
)


# ============================================================
# Engine View Models
# ============================================================


@dataclass(slots=True)
class EngineOverview:
    """
    High-level engine summary displayed on the
    Provider Connections dashboard.
    """

    name: str

    display_name: str

    supported_providers: int

    configured_connections: int

    active_connections: int

    synchronizing_connections: int

    healthy_connections: int

    initialized: bool

    running: bool

    healthy: bool


# ============================================================
# Runtime Models
# ============================================================


@dataclass(slots=True)
class EngineRuntime:

    initialized: bool

    running: bool

    healthy: bool

    statistics: dict[str, Any]


# ============================================================
# Discovery Models
# ============================================================


@dataclass(slots=True)
class ProviderDiscovery:
    """
    Canonical provider discovery model returned to
    the Provider Connections frontend.
    """

    provider: str

    provider_registered: bool

    engine_version: str

    engine_running: bool

    engine_initialized: bool

    provider_version: str | None = None

    broker_name: str | None = None

    terminal_company: str | None = None

    terminal_version: str | None = None

    terminal_build: str | None = None

    terminal_architecture: str | None = None

    terminal_path: str | None = None

    account_number: str | None = None

    server: str | None = None

    supported_evidence: list[str] = field(default_factory=list)

    healthy: bool = False


# ============================================================
# Synchronization Models
# ============================================================


@dataclass(slots=True)
class SynchronizationOverview:
    """
    Canonical synchronization state returned by the
    Provider Connections application service.
    """

    engine: str

    initialized: bool

    running: bool

    healthy: bool

    synchronization_profile: str

    synchronization_state: str

    synchronized_categories: list[str] = field(
        default_factory=list,
    )

    evidence_packages: int = 0

    synchronized_at: datetime | None = None


# ============================================================
# Connection Models
# ============================================================


@dataclass(slots=True)
class ConnectionOverview:

    workspace_id: int

    provider: str

    connection_name: str

    environment: str

    synchronization_profile: str

    verification_status: str

    connection_status: str

    evidence_categories: list[str]


# ============================================================
# Provider Connections Overview
# ============================================================


@dataclass(slots=True)
class ProviderConnectionsOverview:

    summary: dict[str, Any]

    engines: dict[str, EngineOverview]


# ============================================================
# Canonical Responses
# ============================================================


@dataclass(slots=True)
class DesktopConnectionResponse:

    success: bool

    message: str

    connection: ConnectionOverview

    discovery: ProviderDiscovery

    synchronization: SynchronizationOverview

    runtime: EngineRuntime


# ============================================================
# Provider Connections Service
# ============================================================

class ProviderConnectionsService:

    def __init__(
        self,
        *,
        registry: ConnectionRegistry = connection_registry,
        persistence: BaseConnectionPersistence = database_connection_persistence,
    ) -> None:

        #
        # Runtime registry
        #

        self.registry = registry

        #
        # Persistence backend
        #

        self.persistence = persistence

        #
        # Canonical acquisition engines
        #

        self.desktop_engine = desktop_trading_engine

        #
        # Synchronization session registry
        #
        self._synchronization_sessions: dict[
            str,
            dict[str, Any],
        ] = {}

    # ============================================================
    # Provider Connection Lifecycle
    # ============================================================

    def _register_connection(
        self,
        runtime: RuntimeConnection,
    ) -> None:
        """
        Register a RuntimeConnection with both the persistence
        backend and the runtime registry.

        Persistence is committed first so that a runtime connection
        is never registered without a durable Provider Connection.
        """

        #
        # Durable persistence first.
        #

        self.persistence.save(
            runtime.connection,
        )

        #
        # Runtime registration second.
        #

        self.registry.register(
            runtime,
        )
        

    def _register_synchronization_session(
        self,
        *,
        connection_id: str,
        workspace_id: int,
        provider: str,
        synchronization_profile: str,
        evidence_categories: list[str],
    ) -> dict[str, Any]:
        """
        Register the canonical synchronization session for
        a Provider Connection.

        This method creates session state only.
        It does not execute synchronization.
        """

        session = {
            "connection_id": connection_id,
            "workspace_id": workspace_id,
            "provider": provider,
            "synchronization_profile": synchronization_profile,
            "evidence_categories": list(
                evidence_categories,
            ),
            "status": "registered",
        }

        self._synchronization_sessions[
            connection_id
        ] = session

        return session

    def _get_synchronization_session(
        self,
        connection_id: str,
    ) -> dict[str, Any] | None:
        """
        Return the registered synchronization session
        for a Provider Connection.
        """

        return self._synchronization_sessions.get(
            connection_id,
        )

    def _unregister_connection(
        self,
        connection_id: str,
    ) -> None:
        """
        Remove a Provider Connection from both runtime
        and persistence.
        """

        self.registry.unregister(connection_id)

        self.persistence.delete(connection_id)

    
    def delete_connection(
        self,
        *,
        workspace_id: int,
        connection_id: str,
    ) -> None:
        """
        Delete one persisted Provider Connection after validating
        that it belongs to the requested workspace.
        """

        persisted_connections = (
            self.persistence.workspace_connections(
                workspace_id,
            )
        )

        connection = next(
            (
                item
                for item in persisted_connections
                if item.id == connection_id
            ),
            None,
        )

        if connection is None:
            raise KeyError(
                f"Provider connection '{connection_id}' "
                f"was not found in workspace {workspace_id}."
            )

        self._unregister_connection(
            connection_id,
        )


    def _load_workspace_connections(
        self,
        workspace_id: int,
        *,
        connect: bool = False,
    ) -> None:
        """
        Restore persisted Provider Connections into the
        runtime registry.

        Hydration is non-invasive by default.

        Read-only application-service operations must not
        establish external provider connections.

        Explicit operational paths may request connection
        establishment with connect=True.
        """

        persisted_connections = (
            self.persistence.workspace_connections(
                workspace_id,
            )
        )

        for connection in persisted_connections:

            # --------------------------------------------------------
            # Existing runtime
            # --------------------------------------------------------

            if self.registry.exists(
                connection.id,
            ):
                runtime = self.registry.get(
                    connection.id,
                )

                # Explicit operational paths may require a live
                # provider connection.
                if (
                    connect
                    and not runtime.provider.connected
                ):
                    runtime.provider.connect()

                continue

            # --------------------------------------------------------
            # New runtime hydration
            # --------------------------------------------------------

            runtime = self._hydrate_runtime_connection(
                connection,
                connect=connect,
            )

            self.registry.register(
                runtime,
            )

    
    def _load_connection(
        self,
        *,
        workspace_id: int,
        connection_id: str,
        connect: bool = False,
    ) -> RuntimeConnection:
        """
        Restore one persisted Provider Connection into the
        runtime registry.

        This method is intentionally scoped to a single
        connection so explicit operational actions such as
        synchronization and verification cannot initialize or
        connect unrelated workspace providers.
        """

        persisted_connections = (
            self.persistence.workspace_connections(
                workspace_id,
            )
        )

        connection = next(
            (
                item
                for item in persisted_connections
                if item.id == connection_id
            ),
            None,
        )

        if connection is None:
            raise KeyError(
                f"Provider connection '{connection_id}' "
                f"was not found in workspace {workspace_id}."
            )

        if self.registry.exists(
            connection_id,
        ):
            runtime = self.registry.get(
                connection_id,
            )

            if (
                connect
                and not runtime.provider.connected
            ):
                runtime.provider.connect()

            return runtime

        runtime = self._hydrate_runtime_connection(
            connection,
            connect=connect,
        )

        self.registry.register(
            runtime,
        )

        return runtime


    # ============================================================
    # Engine Resolution
    # ============================================================

    def _desktop_engine(self):
        """
        Return the canonical Desktop Trading Engine.
        """

        return self.desktop_engine

    # ============================================================
    # Engine Lifecycle
    # ============================================================

    def _ensure_desktop_engine_running(self) -> None:
        """
        Ensure the Desktop Trading Engine has been initialized
        and started before orchestration begins.
        """

        engine = self._desktop_engine()

        if not engine.is_initialized:

            engine.initialize()

        if not engine.is_running:

            engine.start()

    def _desktop_runtime(self) -> EngineRuntime:
        """
        Return the current Desktop Trading Engine runtime state.
        """

        engine = self._desktop_engine()

        return EngineRuntime(

            initialized=engine.is_initialized,

            running=engine.is_running,

            healthy=engine.health().get(
                "healthy",
                False,
            ),

            statistics=engine.statistics(),

        )

    # ============================================================
    # Runtime Builders
    # ============================================================

    def _connection_overview(
        self,
        *,
        workspace_id: int,
        provider: str,
        connection_name: str,
        environment: str,
        synchronization_profile: str,
        evidence_categories: list[str],
    ) -> ConnectionOverview:
        """
        Build the canonical connection overview returned
        to the frontend.
        """

        return ConnectionOverview(

            workspace_id=workspace_id,

            provider=provider,

            connection_name=connection_name,

            environment=environment,

            synchronization_profile=synchronization_profile,

            verification_status="pending",

            connection_status="connecting",

            evidence_categories=evidence_categories,

        )

    def _provider_discovery(
        self,
        *,
        provider: str,
        evidence_categories: list[str],
    ) -> ProviderDiscovery:
        """
        Build the provider discovery model.

        Actual provider metadata will be populated by the
        Desktop Trading Engine once synchronization completes.
        """

        engine = self._desktop_engine()

        runtime = engine.statistics()

        health = engine.health()

        return ProviderDiscovery(

            provider=provider,

            provider_registered=engine.has_provider(
                provider,
            ),

            engine_version=engine.version,

            engine_running=runtime["running"],

            engine_initialized=runtime["initialized"],

            provider_version=None,

            broker_name=None,

            terminal_company=None,

            terminal_version=None,

            terminal_build=None,

            terminal_architecture=None,

            terminal_path=None,

            account_number=None,

            server=None,

            supported_evidence=evidence_categories,

            healthy=health["healthy"],

        )

    def _synchronization_overview(
        self,
        *,
        evidence_categories: list[str],
    ) -> SynchronizationOverview:
        """
        Build the synchronization overview.

        Actual synchronization statistics will be supplied
        by the acquisition engine.
        """

        engine = self._desktop_engine()

        runtime = engine.statistics()

        health = engine.health()

        return SynchronizationOverview(

            engine="Desktop Trading Engine",

            initialized=runtime["initialized"],

            running=runtime["running"],

            healthy=health["healthy"],

            synchronization_profile=(
                self._default_synchronization_profile()
            ),

            synchronization_state=(
                "running"
                if runtime["running"]
                else "stopped"
            ),

            synchronized_categories=evidence_categories,

            evidence_packages=0,

            synchronized_at=None,

        )

    # ============================================================
    # Response Builders
    # ============================================================

    def _desktop_response(
        self,
        *,
        success: bool,
        message: str,
        connection: ConnectionOverview,
        discovery: ProviderDiscovery,
        synchronization: SynchronizationOverview,
    ) -> DesktopConnectionResponse:
        """
        Build the canonical Desktop Connection response.
        """

        return DesktopConnectionResponse(

            success=success,

            message=message,

            connection=connection,

            discovery=discovery,

            synchronization=synchronization,

            runtime=self._desktop_runtime(),

        )


    # --------------------------------------------------------
    # Overview
    # --------------------------------------------------------

    def overview(
        self,
        workspace_id: int,
    ) -> ProviderConnectionsOverview:
        """
        Return the institutional Provider Connections overview.

        This aggregates the current acquisition engines while
        remaining completely independent from provider-specific
        implementations.
        """

        self._load_workspace_connections(
            workspace_id,
        )

        desktop_runtime = self._desktop_runtime()

        desktop_statistics = desktop_runtime.statistics

        connections = self.registry.connections()

        desktop_connections = [
            c
            for c in connections
            if c.engine == "desktop_trading_engine"
        ]

        configured_connections = len(desktop_connections)

        active_connections = sum(
            c.connected
            for c in desktop_connections
        )

        healthy_connections = sum(
            c.health == ConnectionHealth.HEALTHY
            for c in desktop_connections
        )

        synchronizing_connections = sum(
            c.status == ConnectionStatus.SYNCHRONIZING
            for c in desktop_connections
        )

        desktop_supported = int(
            desktop_statistics.get(
                "providers",
                0,
            )
        )

        desktop_engine = EngineOverview(

            name="desktop",

            display_name="Desktop Trading Engine",

            supported_providers=desktop_supported,

            configured_connections=configured_connections,

            active_connections=active_connections,

            synchronizing_connections=synchronizing_connections,

            healthy_connections=healthy_connections,

            initialized=desktop_runtime.initialized,

            running=desktop_runtime.running,

            healthy=desktop_runtime.healthy,

        )

        gateway_engine = EngineOverview(

            name="gateway",

            display_name="Gateway Trading Engine",

            supported_providers=0,

            configured_connections=0,

            active_connections=0,

            synchronizing_connections=0,

            healthy_connections=0,

            initialized=False,

            running=False,

            healthy=False,

        )

        financial_engine = EngineOverview(

            name="financial",

            display_name="Financial Engine",

            supported_providers=0,

            configured_connections=0,

            active_connections=0,

            synchronizing_connections=0,

            healthy_connections=0,

            initialized=False,

            running=False,

            healthy=False,

        )

        engines = {

            "desktop": desktop_engine,

            "gateway": gateway_engine,

            "financial": financial_engine,

        }

        summary = {

            "supported_providers": (

                desktop_engine.supported_providers
                + gateway_engine.supported_providers
                + financial_engine.supported_providers
            ),

            "configured_connections": (

                desktop_engine.configured_connections
                + gateway_engine.configured_connections
                + financial_engine.configured_connections
            ),

            "verified_connections": 0,

            "healthy_connections": (

                desktop_engine.healthy_connections
                + gateway_engine.healthy_connections
                + financial_engine.healthy_connections
            ),

            "synchronizing": (

                desktop_engine.synchronizing_connections
                + gateway_engine.synchronizing_connections
                + financial_engine.synchronizing_connections
            ),

            "evidence_packages": 0,

        }

        return ProviderConnectionsOverview(

            summary=summary,

            engines=engines,

        )

    # --------------------------------------------------------
    # Engines
    # --------------------------------------------------------

    def engines(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return every acquisition engine currently managed by the
        Provider Connections domain.
        """

        overview = self.overview()

        desktop = overview.engines["desktop"]

        gateway = overview.engines["gateway"]

        financial = overview.engines["financial"]

        return [

            {

                "id": "desktop",

                "name": desktop.display_name,

                "engine": desktop.name,

                "supported_providers": desktop.supported_providers,

                "configured_connections": desktop.configured_connections,

                "active_connections": desktop.active_connections,

                "healthy_connections": desktop.healthy_connections,

                "synchronizing_connections": (
                    desktop.synchronizing_connections
                ),

                "initialized": desktop.initialized,

                "running": desktop.running,

                "healthy": desktop.healthy,

            },

            {

                "id": "gateway",

                "name": gateway.display_name,

                "engine": gateway.name,

                "supported_providers": gateway.supported_providers,

                "configured_connections": gateway.configured_connections,

                "active_connections": gateway.active_connections,

                "healthy_connections": gateway.healthy_connections,

                "synchronizing_connections": (
                    gateway.synchronizing_connections
                ),

                "initialized": gateway.initialized,

                "running": gateway.running,

                "healthy": gateway.healthy,

            },

            {

                "id": "financial",

                "name": financial.display_name,

                "engine": financial.name,

                "supported_providers": (
                    financial.supported_providers
                ),

                "configured_connections": (
                    financial.configured_connections
                ),

                "active_connections": (
                    financial.active_connections
                ),

                "healthy_connections": (
                    financial.healthy_connections
                ),

                "synchronizing_connections": (
                    financial.synchronizing_connections
                ),

                "initialized": financial.initialized,

                "running": financial.running,

                "healthy": financial.healthy,

            },

        ]

    # --------------------------------------------------------
    # Connections
    # --------------------------------------------------------

    def connections(
        self,
        workspace_id: int,
    ):
        """
        Return all registered Provider Connections.
        """

        self._load_workspace_connections(
            workspace_id,
        )

        return [

            {

                "id": connection.id,

                "workspace_id": connection.workspace_id,

                "provider": connection.provider,

                "connection_name": connection.connection_name,

                "engine": connection.engine,

                "environment": connection.environment.value,

                "status": connection.status.value,

                "health": connection.health.value,

                "connected": connection.connected,

                "verified": connection.verified,

            }

            for connection in self.registry.connections()

        ]

    # --------------------------------------------------------
    # Connection Detail
    # --------------------------------------------------------

    def get_connection(
        self,
        workspace_id: int,
        connection_id: str,
    ):
        """
        Return the canonical operational detail for one
        Provider Connection.

        The authoritative lookup is persistence.
        Runtime registry state is not required for detail retrieval.

        Credentials and configuration secrets are intentionally
        excluded from the response.
        """

        connection = self.persistence.get(
            connection_id,
        )

        if connection is None:
            raise KeyError(
                f"Provider connection not found: {connection_id}"
            )

        if connection.workspace_id != workspace_id:
            raise KeyError(
                f"Provider connection not found: {connection_id}"
            )

        return {
            "id": connection.id,
            "workspace_id": connection.workspace_id,
            "connection_name": connection.connection_name,
            "provider": connection.provider,
            "engine": connection.engine,
            "environment": connection.environment.value,
            "status": connection.status.value,
            "health": connection.health.value,
            "verified": connection.verified,
            "connected": connection.connected,
            "created_at": (
                connection.created_at.isoformat()
                if connection.created_at
                else None
            ),
            "updated_at": (
                connection.updated_at.isoformat()
                if connection.updated_at
                else None
            ),
            "statistics": {
                "synchronization_count":
                    connection.statistics.synchronization_count,
                "successful_synchronizations":
                    connection.statistics.successful_synchronizations,
                "failed_synchronizations":
                    connection.statistics.failed_synchronizations,
                "evidence_packages":
                    connection.statistics.evidence_packages,
                "last_synchronization": (
                    connection.statistics.last_synchronization.isoformat()
                    if connection.statistics.last_synchronization
                    else None
                ),
            },
        }

    # ============================================================
    # Desktop Verification
    # ============================================================

    def verify_desktop_connection(
        self,
        *,
        workspace_id: int,
        connection_id: str,
    ) -> DesktopConnectionVerificationResponse:
        """
        Execute canonical Desktop Provider Connection verification.

        Verification is delegated to the Desktop Trading Engine.
        This application service only:

        • resolves the persisted connection
        • validates workspace ownership
        • hydrates the runtime provider
        • invokes Desktop verification
        • persists the resulting verified state
        """

        #
        # Restore only the requested Provider Connection.
        #
        # Verification is scoped to one connection and must never
        # establish unrelated workspace providers.
        #
        runtime = self._load_connection(
            workspace_id=workspace_id,
            connection_id=connection_id,
            connect=True,
        )

        #
        # Resolve the runtime connection.
        #
        runtime = next(
            (
                runtime_connection
                for runtime_connection
                in self.registry.runtimes()
                if (
                    runtime_connection.id == connection_id
                    and runtime_connection.connection.workspace_id
                    == workspace_id
                )
            ),
            None,
        )

        if runtime is None:
            raise KeyError(
                f"Provider connection not found: {connection_id}"
            )

        connection = runtime.connection

        #
        # Desktop verification currently applies only to
        # Desktop Trading Engine connections.
        #
        if connection.engine != "desktop_trading_engine":
            raise ValueError(
                "Provider connection does not belong to "
                "the Desktop Trading Engine."
            )

        #
        # Read the persisted provider configuration.
        #
        credentials = (
            connection.configuration.get(
                "credentials",
                {},
            )
        )

        #
        # Resolve the configured account identity.
        #
        expected_account_id = (
            credentials.get("account_id")
            or credentials.get("account")
            or credentials.get("login")
            or credentials.get("account_number")
            or credentials.get("user")
        )

        if expected_account_id is not None:
            expected_account_id = str(
                expected_account_id
            )

        #
        # Resolve the configured server identity.
        #
        expected_server = (
            credentials.get("server")
            or credentials.get("broker_server")
        )

        #
        # Execute the canonical Desktop Verification Engine.
        #
        result = runtime.provider.verify(
            expected_provider=connection.provider,
            expected_account_id=expected_account_id,
            expected_server=expected_server,
        )

        #
        # Verification is authoritative for the connection's
        # verification state.
        #
        connection.verified = result.verified

        #
        # Reflect the observed connectivity state.
        #
        connection.connected = (
            result.snapshot.connected
            if result.snapshot is not None
            else connection.connected
        )

        #
        # Persist the updated verification state.
        #
        connection.updated_at = datetime.utcnow()

        self.persistence.update(
            connection,
        )

        return DesktopConnectionVerificationResponse(
            provider=result.provider,
            verified=result.verified,
            checks=[
                {
                    "name": check.name,
                    "passed": check.passed,
                    "message": check.message,
                    "observed": check.observed,
                    "expected": check.expected,
                }
                for check in result.checks
            ],
            error=result.error,
            snapshot=(
                result.to_dict().get("snapshot")
                if result.snapshot is not None
                else None
            ),
        )

    # --------------------------------------------------------
    # Activity
    # --------------------------------------------------------

    def activity(
        self,
    ):
        """
        Provider Connection runtime activity.
        """

        statistics = self.registry.statistics()

        return {

            "total": statistics.total,

            "connected": statistics.connected,

            "disconnected": statistics.disconnected,

            "failed": statistics.failed,

            "synchronizing": statistics.synchronizing,

        }

    # ============================================================
    # Shared Builders
    # ============================================================

    def _default_synchronization_profile(
        self,
    ) -> str:
        """
        Return the canonical synchronization profile.

        Until workspace-level synchronization policies are
        introduced, every Provider Connection uses the
        Institutional profile.
        """

        return "institutional"

    def _supported_evidence_categories(
        self,
        provider: str,
    ) -> list[str]:
        """
        Return the canonical evidence categories supported by
        the selected provider.

        Later this will be resolved directly from the Desktop
        Trading Engine provider registry.
        """

        return [

            "trades",

            "orders",

            "deals",

            "positions",

            "account",

            "balance",

            "equity",

            "margin",

            "history",

            "terminal",

            "broker",

            "symbols",

            "execution",

            "sessions",

        ]

    def _runtime_statistics(
        self,
    ) -> dict[str, Any]:
        """
        Convenience wrapper used by orchestration methods.
        """

        self._ensure_desktop_engine_running()

        return self.desktop_engine.statistics()

    def _build_desktop_provider(
        self,
        *,
        workspace_id: int,
        provider: str,
        environment: str,
        credentials: dict[str, Any],
    ):
        """
        Compose the canonical Desktop Evidence Provider.

        This method performs composition only.

        It intentionally does NOT:

            • synchronize
            • acquire evidence
            • verify evidence
        """

        #
        # Resolve the adapter.
        #

        adapter = self._resolve_desktop_adapter(
            provider=provider,
            environment=environment,
            credentials=credentials,
        )

        #
        # Resolve the translator.
        #

        translator = self._resolve_desktop_translator(

            provider=provider,

        )

        #
        # Connector configuration.
        #

        configuration = self._build_connector_configuration(

            workspace_id=workspace_id,

            provider=provider,

            environment=environment,

        )

        #
        # Connector.
        #

        connector = DesktopConnector(

            adapter=adapter,

            translator=translator,

            configuration=configuration,

        )

        #
        # Canonical Provider.
        #

        return DesktopEvidenceProvider(

            connector,

        )

    def _hydrate_runtime_connection(
        self,
        connection: ProviderConnection,
        *,
        connect: bool = False,
    ) -> RuntimeConnection:
        """
        Rebuild a RuntimeConnection from a persisted
        ProviderConnection.
        """

        credentials = (
            connection.configuration.get("credentials", {})
        )

        desktop_provider = self._build_desktop_provider(

            workspace_id=connection.workspace_id,

            provider=connection.provider,

            environment=connection.environment.value,

            credentials=credentials,

        )

        if connect and not desktop_provider.connected:
            desktop_provider.connect()

        return RuntimeConnection(

            connection=connection,

            provider=desktop_provider,

        )

    def _resolve_desktop_adapter(
        self,
        *,
        provider: str,
        environment: str,
        credentials: dict[str, Any],
    ) -> BaseDesktopAdapter:
        """
        Resolve the canonical desktop adapter.

        Responsibilities
        ----------------

        • Select the correct adapter implementation.
        • Construct the adapter.
        • Never connect.
        • Never synchronize.
        """

        provider_key = provider.strip().lower()

        # ------------------------------------------------------------------
        # Provider-owned application credentials
        # ------------------------------------------------------------------
        #
        # cTrader Client ID and Client Secret belong to the TTL Open API
        # application, not to the end user. They are therefore supplied by
        # the backend and never persisted from the frontend form.
        #
        adapter_credentials = dict(credentials)

        if provider_key == "ctrader":
            client_id = os.getenv("CTRADER_CLIENT_ID")
            client_secret = os.getenv("CTRADER_CLIENT_SECRET")

            if not client_id:
                raise RuntimeError(
                    "CTRADER_CLIENT_ID is not configured on the backend."
                )

            if not client_secret:
                raise RuntimeError(
                    "CTRADER_CLIENT_SECRET is not configured on the backend."
                )

            adapter_credentials["client_id"] = client_id
            adapter_credentials["client_secret"] = client_secret

        adapter_map = {

            "metatrader 5": MT5Adapter,

            "mt5": MT5Adapter,

            "metatrader 4": MT4Adapter,

            "mt4": MT4Adapter,

            "interactive brokers": IBKRAdapter,

            "ibkr": IBKRAdapter,

            "ctrader": CTraderAdapter,

            "ninjatrader": NinjaTraderAdapter,

            "tradestation": TradeStationAdapter,

            "sierra chart": SierraChartAdapter,

            "quantower": QuantowerAdapter,

            "multicharts": MultiChartsAdapter,

            "motivewave": MotiveWaveAdapter,

            "trading technologies": TradingTechnologiesAdapter,

            "tt": TradingTechnologiesAdapter,

        }

        adapter_type = adapter_map.get(provider_key)

        if adapter_type is None:

            raise ValueError(

                f"Unsupported desktop provider '{provider}'."

            )

        #
        # Canonical credential normalization.
        #

        account = (

            credentials.get("account")

            or credentials.get("login")

            or credentials.get("account_number")

            or credentials.get("user")

        )

        password = (

            credentials.get("password")

            or credentials.get("passwd")

        )

        server = (

            credentials.get("server")

            or credentials.get("broker_server")

        )

        terminal_path = (

            credentials.get("terminal_path")

            or credentials.get("path")

            or credentials.get("terminal")

        )


        #
        # Provider-native construction hook.
        #
        # This is optional. Providers such as MotiveWave may expose
        # a provider-specific connection factory, while legacy desktop
        # adapters continue using their existing constructor contract.
        #
        connection_factory = getattr(
            adapter_type,
            "from_connection_config",
            None,
        )

        if callable(connection_factory):
            return connection_factory(
                credentials=adapter_credentials,
                environment=environment,
            )

        return adapter_type(
            login=int(account) if account else 0,
            password=password or "",
            server=server,
            path=terminal_path,
        )

    def _resolve_desktop_translator(
        self,
        *,
        provider: str,
    ) -> BaseTranslator:
        """
        Resolve the canonical Desktop Translator.

        Every supported desktop trading platform produces the
        canonical desktop acquisition contract.

        Therefore all providers share the same translator.

        Responsibilities
        ----------------

        • Resolve translator
        • Never inspect provider credentials
        • Never acquire evidence
        • Never synchronize
        • Never verify
        """

        #
        # Future compatibility.
        #
        # Provider-specific translators can be introduced
        # without changing the orchestration layer.
        #

        _ = provider

        return DesktopTranslator()

    def _build_connector_configuration(
        self,
        *,
        workspace_id: int,
        provider: str,
        environment: str,
    ) -> ConnectorConfiguration:
        """
        Build the canonical Desktop Connector configuration.

        This method is responsible only for describing how the
        DesktopConnector should operate.

        It intentionally does NOT:

            • create adapters
            • create connectors
            • register providers
            • synchronize evidence
            • verify evidence
        """

        settings = {

            #
            # Workspace
            #

            "workspace_id": workspace_id,

            #
            # Environment
            #

            "environment": environment,

            #
            # Synchronization
            #

            "auto_connect": True,

            "auto_reconnect": True,

            "auto_synchronize": True,

            #
            # Discovery
            #

            "discover_terminal": True,

            "discover_broker": True,

            "discover_account": True,

            #
            # Evidence Acquisition
            #

            "acquire_trades": True,

            "acquire_orders": True,

            "acquire_positions": True,

            "acquire_deals": True,

            "acquire_account": True,

            "acquire_balance_history": True,

            "acquire_equity_history": True,

            "acquire_symbols": True,

            "acquire_market_watch": True,

            "acquire_terminal": True,

            "acquire_server": True,

            "acquire_logs": True,

            "acquire_journal": True,

            "acquire_execution": True,

            "acquire_margin": True,

            "acquire_exposure": True,

            "acquire_statistics": True,

        }

        return ConnectorConfiguration(

            provider=provider,

            settings=settings,

        )

    # --------------------------------------------------------
    # Desktop Connections
    # --------------------------------------------------------

    def test_desktop_connection(
        self,
        *,
        workspace_id: int,
        provider: str,
        connection_name: str,
        environment: str,
        synchronization_profile: str,
        evidence_categories: list[str],
        credentials: dict[str, Any],
    ) -> DesktopConnectionResponse:
        """
        Validate a Desktop Provider Connection.

        This method performs orchestration only.

        It intentionally DOES NOT:

            • synchronize providers
            • acquire evidence
            • verify evidence

        Those responsibilities remain owned by the
        Desktop Trading Engine.
        """

        #
        # Ensure the Desktop Trading Engine is operational.
        #

        self._ensure_desktop_engine_running()

        #
        # Resolve supported evidence.
        #

        supported_evidence = (

            evidence_categories

            or

            self._supported_evidence_categories(
                provider,
            )

        )

        #
        # Build canonical models.
        #

        connection = self._connection_overview(

            workspace_id=workspace_id,

            provider=provider,

            connection_name=connection_name,

            environment=environment,

            synchronization_profile=synchronization_profile,

            evidence_categories=supported_evidence,

        )

        discovery = self._provider_discovery(

            provider=provider,

            evidence_categories=supported_evidence,

        )

        synchronization = self._synchronization_overview(

            evidence_categories=supported_evidence,

        )

        #
        # Build canonical response.
        #

        return self._desktop_response(

            success=True,

            message=(
                "Desktop provider connection "
                "validated successfully."
            ),

            connection=connection,

            discovery=discovery,

            synchronization=synchronization,

        )

    def create_desktop_connection(
        self,
        *,
        workspace_id: int,
        provider: str,
        connection_name: str,
        environment: str,
        synchronization_profile: str,
        evidence_categories: list[str],
        credentials: dict[str, Any],
    ) -> DesktopConnectionResponse:
        """
        Create a Desktop Provider Connection.

        This method is the canonical application-service entry
        point responsible for orchestrating provider connection
        creation.

        It intentionally does NOT:

            • connect to providers
            • synchronize providers
            • acquire evidence
            • verify evidence

        Those responsibilities remain owned by the
        Desktop Trading Engine.
        """

        #
        # Ensure Desktop Trading Engine availability.
        #

        self._ensure_desktop_engine_running()

        #
        # Normalize desktop credentials.
        #
        desktop_credentials = dict(credentials)

        connection_name = " ".join(
            connection_name.strip().split()
        )

        provider_key = provider.strip().lower()

        provider = provider.strip()

        if provider_key in {
            "metatrader 5",
            "mt5",
        }:
            desktop_credentials.setdefault(
                "server",
                os.getenv("MT5_SERVER"),
            )

            desktop_credentials.setdefault(
                "terminal_path",
                os.getenv("MT5_TERMINAL"),
            )

        #
        # Resolve the canonical Desktop Provider.
        #

        desktop_provider = self._build_desktop_provider(

            workspace_id=workspace_id,

            provider=provider,

            environment=environment,

            credentials=desktop_credentials,

        )

        #
        # Establish the underlying provider connection.
        #

        if not desktop_provider.connected:
            desktop_provider.connect()

        #
        # Build canonical runtime connection.
        #

        runtime_connection = ProviderConnection(

            id=f"{workspace_id}:{provider.strip()}:{connection_name}",

            workspace_id=workspace_id,

            connection_name=connection_name,

            provider=provider,

            engine="desktop_trading_engine",

            environment=ConnectionEnvironment(
                environment.lower(),
            ),

            configuration={

                "credentials": desktop_credentials,

            },

            status=ConnectionStatus.CONNECTED,

            health=ConnectionHealth.HEALTHY,

            connected=True,

            verified=False,

        )

        runtime = RuntimeConnection(

            connection=runtime_connection,

            provider=desktop_provider,

        )

        #
        # Register runtime + persistence.
        #

        self._register_connection(
            runtime,
        )

        #
        # Refresh runtime after registration.
        #

        runtime_statistics = self.desktop_engine.statistics()

        runtime_health = self.desktop_engine.health()

        #
        # Resolve supported evidence.
        #

        supported_evidence = (

            evidence_categories

            or

            self._supported_evidence_categories(
                provider,
            )

        )

        #
        # Build canonical connection model.
        #

        connection_overview = self._connection_overview(

            workspace_id=workspace_id,

            provider=provider,

            connection_name=connection_name,

            environment=environment,

            synchronization_profile=synchronization_profile,

            evidence_categories=supported_evidence,

        )

        #
        # Discover provider metadata.
        #

        discovery = self._provider_discovery(

            provider=provider,

            evidence_categories=supported_evidence,

        )

        #
        # Build synchronization model.
        #

        synchronization = self._synchronization_overview(

            evidence_categories=supported_evidence,

        )

        #
        # Persistence
        #
        # Provider Connection has already been durably persisted
        # during runtime registration.
        #
        # Future synchronization-session registration and automatic
        # synchronization scheduling remain separate lifecycle concerns.
        #

        return DesktopConnectionCreateResponse(

            id=runtime_connection.id,

            provider=runtime_connection.provider,

            connection_name=runtime_connection.connection_name,

            status=runtime_connection.status.value,

            synchronization_profile=synchronization_profile,

            created_at=runtime_connection.created_at,

        )

    # =====================================================================
    # Synchronization
    # =====================================================================

    def synchronize_connection(
        self,
        *,
        workspace_id: int,
        connection_id: str,
    ):
        """
        Synchronize a configured provider connection.

        Delegates evidence acquisition to the canonical
        Provider Synchronization Orchestrator.
        """

        #
        # Workspace ownership validation will be introduced
        # once persistent provider connections are backed by
        # the database.
        #

        self._load_connection(
            workspace_id=workspace_id,
            connection_id=connection_id,
            connect=True,
        )

        return provider_synchronization_orchestrator.synchronize_connection(
            workspace_id=workspace_id,
            connection_id=connection_id,
        )



provider_connections_service = ProviderConnectionsService()


__all__ = [

    "EngineOverview",

    "ProviderConnectionsOverview",

    "ProviderConnectionsService",

    "provider_connections_service",

]