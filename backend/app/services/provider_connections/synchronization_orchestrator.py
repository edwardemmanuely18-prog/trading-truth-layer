"""
Trading Truth Layer (TTL)

Provider Synchronization Orchestrator

Canonical orchestration layer between the Provider Connections domain
and the Evidence Acquisition Runtime.

Responsibilities
----------------
• Resolve provider connections
• Build acquisition connectors
• Invoke Evidence Acquisition engines
• Return synchronization results

The orchestrator intentionally does NOT:

• Acquire evidence directly
• Translate evidence
• Canonicalize evidence
• Verify evidence
• Publish evidence

Those responsibilities remain owned by the
Evidence Acquisition Runtime and Universal Evidence Adapter.
"""

from __future__ import annotations

from app.services.evidence_acquisition.desktop_trading_engine.engine import (
    desktop_trading_engine,
)

from .registry import (
    connection_registry,
)

from .models import ProviderConnection

from app.services.evidence_acquisition.desktop_trading_engine.desktop_connector import (
    DesktopConnector,
)


# ============================================================================
# Provider Synchronization Orchestrator
# ============================================================================

class ProviderSynchronizationOrchestrator:
    """
    Canonical orchestration layer responsible for coordinating
    provider synchronization across the Evidence Acquisition Runtime.
    """

    def __init__(self) -> None:

        self.registry = connection_registry

        self.desktop_engine = desktop_trading_engine

    # =====================================================================
    # Synchronization
    # =====================================================================

    # =====================================================================
    # Connection Resolution
    # =====================================================================

    def _resolve_connection(
        self,
        connection_id: str,
    ):
        """
        Resolve a RuntimeConnection from the canonical registry.

        Raises
        ------
        KeyError
            If the requested runtime connection does not exist.
        """

        if not self.registry.exists(connection_id):

            raise KeyError(

                f"Provider Connection '{connection_id}' does not exist."

            )

        return self.registry.get(
            connection_id,
        )


    # ============================================================================
    # Engine Invocation
    # ============================================================================

    def _synchronize_desktop_connection(
        self,
        *,
        workspace_id: int,
        connector: DesktopConnector,
    ):
        """
        Execute the complete Desktop Trading Engine synchronization
        pipeline.

        Ownership remains inside the Desktop Trading Engine.

        Broker
            ↓
        Desktop Synchronizer
            ↓
        Desktop Evidence Package
            ↓
        Raw Evidence
            ↓
        Universal Evidence Adapter
        """

        return self.desktop_engine.synchronize_evidence(
            connector,
            workspace_id=workspace_id,
        )

    def synchronize_connection(
        self,
        *,
        workspace_id: int,
        connection_id: str,
    ):
        """
        Synchronize a single provider connection.
        """

        runtime = self._resolve_connection(
            connection_id,
        )
    
        result = self._synchronize_desktop_connection(
            workspace_id=workspace_id,
            connector=runtime.provider.connector,
        )

        return result


# ============================================================================
# Global Orchestrator
# ============================================================================

provider_synchronization_orchestrator = (
    ProviderSynchronizationOrchestrator()
)


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "ProviderSynchronizationOrchestrator",
    "provider_synchronization_orchestrator",
]