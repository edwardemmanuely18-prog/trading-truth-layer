"""
Trading Truth Layer (TTL)

Evidence Acquisition

Application Service

Institutional application service responsible for exposing
Evidence Acquisition capabilities to the API layer.

Responsibilities
----------------
• Aggregate runtime information
• Aggregate bridge information
• Aggregate provider information
• Produce frontend view models

This service intentionally DOES NOT:

• acquire evidence
• synchronize providers
• normalize evidence
• validate evidence
• publish evidence
• verify evidence

Those responsibilities remain inside the Runtime,
Acquisition Bridge and Universal Evidence Adapter.
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from typing import Any
from typing import Dict

from .acquisition_bridge import (
    AcquisitionBridge,
    BridgeHealth,
    BridgeStatistics,
)

from .provider_registry import (
    ProviderStatistics,
)

from .runtime import (
    EvidenceAcquisitionRuntime,
    RuntimeStatistics,
)

from app.services.provider_connections.service import (
    provider_connections_service,
)


# ============================================================================
# View Models
# ============================================================================


@dataclass(slots=True)
class EngineSummary:

    registered: bool

    healthy: bool


@dataclass(slots=True)
class OverviewSummary:

    summary: Dict[str, Any]

    runtime: Dict[str, Any]

    providers: Dict[str, Any]

    bridge: Dict[str, Any]

    engines: Dict[str, EngineSummary]


# ============================================================================
# Service
# ============================================================================


class EvidenceAcquisitionService:
    """
    Canonical application service for Evidence Acquisition.

    The frontend should communicate only with this service.
    """

    def __init__(
        self,
        runtime: EvidenceAcquisitionRuntime,
        bridge: AcquisitionBridge,
    ) -> None:

        self.runtime = runtime

        self.bridge = bridge

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    def overview(self) -> OverviewSummary:
        """
        Overview consumed by the institutional dashboard.
        """

        runtime: RuntimeStatistics = self.runtime.statistics

        providers: ProviderStatistics = (
            self.runtime.providers.statistics()
        )

        bridge_statistics: BridgeStatistics = (
            self.bridge.statistics()
        )

        bridge_health: BridgeHealth = (
            self.bridge.health()
        )

        return OverviewSummary(

            summary={

                "connected_sources":
                    runtime.active_connections,

                "registered_adapters":
                    providers.total,

                "active_synchronizations":
                    runtime.synchronization_jobs,

                "evidence_packages":
                    0,

            },

            runtime={

                "state":
                    self.runtime.information.state.value,

                "registered_engines":
                    runtime.registered_engines,

                "running_engines":
                    runtime.running_engines,

                "active_connections":
                    runtime.active_connections,

                "synchronization_jobs":
                    runtime.synchronization_jobs,

            },

            providers=asdict(providers),

            bridge={

                **asdict(bridge_statistics),

                **asdict(bridge_health),

            },

            engines={

                "gateway": EngineSummary(

                    registered=
                        bridge_statistics.gateway_registered,

                    healthy=
                        bridge_health.gateway,

                ),

                "desktop": EngineSummary(

                    registered=
                        bridge_statistics.desktop_registered,

                    healthy=
                        bridge_health.desktop,

                ),

                "financial": EngineSummary(

                    registered=
                        bridge_statistics.financial_registered,

                    healthy=
                        bridge_health.financial,

                ),

            },

        )

    # ------------------------------------------------------------------
    # Placeholders
    # ------------------------------------------------------------------

    def sources(
        self,
        workspace_id: int,
    ) -> list[dict[str, Any]]:
        """
        Canonical provider registry consumed by the Sources page.

        Provider definitions come from the Evidence Acquisition
        provider registry.

        Operational connection state comes from the canonical
        Provider Connections service.

        A provider is not itself a connection. Therefore:
            - provider.certified describes provider capability
            - provider.active describes provider registry state
            - configured_connections describes actual configured instances
            - connected describes whether at least one configured
            connection is connected
            - healthy describes whether at least one configured
            connection is healthy
        """

        providers = self.runtime.providers.providers()

        connections = (
            provider_connections_service.connections(
                workspace_id,
            )
        )

        connection_by_provider: dict[str, list[dict[str, Any]]] = {}

        for connection in connections:
            provider_name = (
                str(
                    connection.get(
                        "provider",
                        "",
                    )
                )
                .strip()
                .lower()
            )

            connection_by_provider.setdefault(
                provider_name,
                [],
            ).append(connection)

        result: list[dict[str, Any]] = []

        for provider in providers:

            provider_name = (
                str(provider.name)
                .strip()
                .lower()
            )

            provider_connections = (
                connection_by_provider.get(
                    provider_name,
                    [],
                )
            )

            configured_connections = (
                len(provider_connections)
            )

            connected_connections = sum(
                bool(
                    connection.get(
                        "connected",
                        False,
                    )
                )
                for connection in provider_connections
            )

            healthy_connections = sum(
                connection.get(
                    "health",
                    "",
                ) == "healthy"
                for connection in provider_connections
            )

            verified_connections = sum(
                bool(
                    connection.get(
                        "verified",
                        False,
                    )
                )
                for connection in provider_connections
            )

            active = (
                configured_connections > 0
                and connected_connections > 0
            )

            connected = (
                connected_connections > 0
            )

            healthy = (
                healthy_connections > 0
            )

            if healthy:
                state = "healthy"
            elif connected:
                state = "connected"
            elif configured_connections > 0:
                state = "configured"
            else:
                state = provider.state.value

            result.append(
                {
                    "name": provider.name,

                    "engine": provider.engine,

                    "provider_type": (
                        provider.metadata.get(
                            "provider_type",
                            "Unknown",
                        )
                    ),

                    "certified": provider.certified,

                    "active": active,

                    "connected": connected,

                    "state": state,

                    "configured_connections": (
                        configured_connections
                    ),

                    "connected_connections": (
                        connected_connections
                    ),

                    "healthy_connections": (
                        healthy_connections
                    ),

                    "verified_connections": (
                        verified_connections
                    ),
                }
            )

        return result

    def synchronizations(self):

        return {}

    def diagnostics(self):

        return {}


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "EngineSummary",

    "OverviewSummary",

    "EvidenceAcquisitionService",

]