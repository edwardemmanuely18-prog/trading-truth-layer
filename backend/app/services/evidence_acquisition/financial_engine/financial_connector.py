"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Connector Manager

Institutional connector orchestration for the Financial
Infrastructure Engine.

This module manages the lifecycle of every registered
Financial Connector.

Responsibilities

• Registration
• Connection lifecycle
• Authentication
• Health monitoring
• Bulk operations
• Synchronization readiness
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Dict
from typing import List
from typing import Optional

from .connectors import (
    ConnectionState,
    ConnectorDiagnostics,
    ConnectorRegistry,
    FinancialConnector,
)


# ============================================================================
# Financial Engine Health
# ============================================================================


@dataclass(slots=True)
class FinancialEngineHealth:
    """
    Runtime health snapshot for the Financial Engine.
    """

    provider_count: int

    connected: int

    authenticated: int

    degraded: int

    failed: int

    synchronization_ready: bool


# ============================================================================
# Financial Connector Manager
# ============================================================================


class FinancialConnectorManager:
    """
    Central connector orchestration service.
    """

    def __init__(self) -> None:

        self._registry = ConnectorRegistry()

    # ---------------------------------------------------------------------
    # Registration
    # ---------------------------------------------------------------------

    def register(
        self,
        connector: FinancialConnector,
    ) -> None:

        self._registry.register(connector)

    def unregister(
        self,
        provider: str,
    ) -> None:

        self._registry.unregister(provider)

    # ---------------------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------------------

    def connector(
        self,
        provider: str,
    ) -> Optional[FinancialConnector]:

        return self._registry.connector(provider)

    def providers(self) -> List[str]:

        return self._registry.providers()

    def connectors(self) -> List[FinancialConnector]:

        return self._registry.connectors()

    # ---------------------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------------------

    def connect(
        self,
        provider: str,
    ) -> None:

        connector = self.connector(provider)

        if connector is None:
            return

        connector.connect()

    def authenticate(
        self,
        provider: str,
    ) -> None:

        connector = self.connector(provider)

        if connector is None:
            return

        connector.authenticate()

    def disconnect(
        self,
        provider: str,
    ) -> None:

        connector = self.connector(provider)

        if connector is None:
            return

        connector.disconnect()

    # ---------------------------------------------------------------------
    # Bulk Lifecycle
    # ---------------------------------------------------------------------

    def connect_all(self) -> None:

        for connector in self.connectors():

            connector.connect()

    def authenticate_all(self) -> None:

        for connector in self.connectors():

            connector.authenticate()

    def disconnect_all(self) -> None:

        for connector in self.connectors():

            connector.disconnect()

    # ---------------------------------------------------------------------
    # Monitoring
    # ---------------------------------------------------------------------

    def health_check(
        self,
        provider: str,
    ) -> bool:

        connector = self.connector(provider)

        if connector is None:
            return False

        return connector.health_check()

    def health_check_all(
        self,
    ) -> Dict[str, bool]:

        results: Dict[str, bool] = {}

        for connector in self.connectors():

            results[
                connector.provider_name()
            ] = connector.health_check()

        return results

    def ping(
        self,
        provider: str,
    ) -> Optional[float]:

        connector = self.connector(provider)

        if connector is None:
            return None

        return connector.ping()

    # ---------------------------------------------------------------------
    # Status
    # ---------------------------------------------------------------------

    def state(
        self,
        provider: str,
    ) -> Optional[ConnectionState]:

        connector = self.connector(provider)

        if connector is None:
            return None

        return connector.connection.state

    def connected(
        self,
        provider: str,
    ) -> bool:

        connector = self.connector(provider)

        if connector is None:
            return False

        return connector.connected

    def authenticated(
        self,
        provider: str,
    ) -> bool:

        connector = self.connector(provider)

        if connector is None:
            return False

        return connector.authenticated

    # ---------------------------------------------------------------------
    # Synchronization
    # ---------------------------------------------------------------------

    def synchronization_ready(self) -> bool:

        if self._registry.count() == 0:

            return False

        return all(

            connector.authenticated

            for connector in self.connectors()

        )

    # ---------------------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> ConnectorDiagnostics:

        connected = 0

        authenticated = 0

        degraded = 0

        failed = 0

        for connector in self.connectors():

            state = connector.connection.state

            if state in (
                ConnectionState.CONNECTED,
                ConnectionState.AUTHENTICATED,
            ):
                connected += 1

            if state == ConnectionState.AUTHENTICATED:
                authenticated += 1

            elif state == ConnectionState.DEGRADED:
                degraded += 1

            elif state == ConnectionState.FAILED:
                failed += 1

        return ConnectorDiagnostics(
            provider_count=self._registry.count(),
            connected=connected,
            authenticated=authenticated,
            degraded=degraded,
            failed=failed,
        )

    def health(self) -> FinancialEngineHealth:

        diagnostics = self.diagnostics()

        return FinancialEngineHealth(
            provider_count=diagnostics.provider_count,
            connected=diagnostics.connected,
            authenticated=diagnostics.authenticated,
            degraded=diagnostics.degraded,
            failed=diagnostics.failed,
            synchronization_ready=self.synchronization_ready(),
        )

    # ---------------------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------------------

    def connector_count(self) -> int:

        return self._registry.count()

    def clear(self) -> None:

        self._registry.clear()


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [
    "FinancialEngineHealth",
    "FinancialConnectorManager",
]