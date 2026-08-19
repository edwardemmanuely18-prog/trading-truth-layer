"""
Trading Truth Layer (TTL)

Provider Connections

Connection Registry

Canonical registry responsible for managing configured
provider connections.

This registry owns RuntimeConnection objects.

Each RuntimeConnection contains

• ProviderConnection
• DesktopEvidenceProvider

The registry exposes ProviderConnection objects publicly while
retaining runtime objects internally.

It does not:

• connect providers
• synchronize evidence
• create adapters
• create connectors

Those responsibilities remain inside the
Evidence Acquisition subsystem.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
from typing import List

from .models import (
    ConnectionStatus,
    ProviderConnection,
    RuntimeConnection,
)


# ============================================================
# Statistics
# ============================================================


@dataclass(slots=True)
class ConnectionRegistryStatistics:

    total: int = 0

    connected: int = 0

    disconnected: int = 0

    synchronizing: int = 0

    failed: int = 0


# ============================================================
# Registry
# ============================================================


class ConnectionRegistry:
    """
    Canonical registry for configured provider connections.
    """

    def __init__(self) -> None:

        self._connections: Dict[str, RuntimeConnection] = {}

    # --------------------------------------------------------
    # Registration
    # --------------------------------------------------------

    def register(
        self,
        runtime: RuntimeConnection,
    ) -> None:

        print("=" * 80)
        print("REGISTERING CONNECTION")
        print("=" * 80)
        print("Runtime ID :", runtime.id)
        print("=" * 80)

        self._connections[runtime.id] = runtime


    def unregister(
        self,
        connection_id: str,
    ) -> None:

        self._connections.pop(connection_id, None)

    # --------------------------------------------------------
    # Lookup
    # --------------------------------------------------------

    def exists(
        self,
        connection_id: str,
    ) -> bool:

        print("=" * 80)
        print("EXISTS CHECK")
        print("=" * 80)
        print("Requested :", connection_id)
        print("Available :", list(self._connections.keys()))
        print("=" * 80)

        return connection_id in self._connections

    def get(
        self,
        connection_id: str,
    ) -> RuntimeConnection:

        print("=" * 80)
        print("LOOKUP CONNECTION")
        print("=" * 80)
        print("Requested :", connection_id)
        print("Available :", list(self._connections.keys()))
        print("=" * 80)

        return self._connections[connection_id]

    def runtimes(
        self,
    ) -> List[RuntimeConnection]:
        """
        Return all runtime connections.
        """

        return list(
            self._connections.values(),
        )


    def connections(
        self,
    ) -> List[ProviderConnection]:
        """
        Return configured provider connections.
        """

        return [

            runtime.connection

            for runtime in self._connections.values()

        ]

    # --------------------------------------------------------
    # Filters
    # --------------------------------------------------------

    def connected(
        self,
    ) -> List[ProviderConnection]:

        return [

            runtime.connection

            for runtime in self._connections.values()

            if runtime.connection.connected

        ]

    def failed(
        self,
    ) -> List[ProviderConnection]:

        return [

            runtime.connection

            for runtime in self._connections.values()

            if runtime.connection.status == ConnectionStatus.FAILED

        ]

    def synchronizing(
        self,
    ) -> List[ProviderConnection]:

        return [

            runtime.connection

            for runtime in self._connections.values()

            if runtime.connection.status == ConnectionStatus.SYNCHRONIZING

        ]

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    def statistics(
        self,
    ) -> ConnectionRegistryStatistics:

        connections = [

            runtime.connection

            for runtime in self._connections.values()

        ]

        return ConnectionRegistryStatistics(

            total=len(connections),

            connected=sum(

                connection.connected

                for connection in connections

            ),

            disconnected=sum(

                not connection.connected

                for connection in connections

            ),

            synchronizing=sum(

                connection.status == ConnectionStatus.SYNCHRONIZING

                for connection in connections

            ),

            failed=sum(

                connection.status == ConnectionStatus.FAILED

                for connection in connections

            ),

        )

    # --------------------------------------------------------
    # Utilities
    # --------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._connections.clear()

    
# ============================================================
# Global Registry
# ============================================================

connection_registry = ConnectionRegistry()


# ============================================================
# Public Exports
# ============================================================

__all__ = [

    "ConnectionRegistryStatistics",

    "ConnectionRegistry",

    "connection_registry",

]