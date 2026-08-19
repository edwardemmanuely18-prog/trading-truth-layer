"""
Trading Truth Layer (TTL)

Provider Connections

In-Memory Persistence

Reference implementation of the canonical persistence contract.

This implementation is intended for:

    • development
    • testing
    • bootstrapping

It may later be replaced by a database-backed implementation
without changing the Provider Connections Service.
"""

from __future__ import annotations

from typing import Dict
from typing import List
from typing import Optional

from ..models import ProviderConnection
from .base import BaseConnectionPersistence


# ============================================================
# Memory Persistence
# ============================================================


class MemoryConnectionPersistence(BaseConnectionPersistence):
    """
    In-memory Provider Connection persistence.
    """

    def __init__(self) -> None:

        self._connections: Dict[str, ProviderConnection] = {}

    # --------------------------------------------------------
    # CRUD
    # --------------------------------------------------------

    def save(
        self,
        connection: ProviderConnection,
    ) -> None:

        self._connections[connection.id] = connection

    def update(
        self,
        connection: ProviderConnection,
    ) -> None:

        self._connections[connection.id] = connection

    def delete(
        self,
        connection_id: str,
    ) -> None:

        self._connections.pop(connection_id, None)

    # --------------------------------------------------------
    # Lookup
    # --------------------------------------------------------

    def get(
        self,
        connection_id: str,
    ) -> Optional[ProviderConnection]:

        return self._connections.get(connection_id)

    def exists(
        self,
        connection_id: str,
    ) -> bool:

        return connection_id in self._connections

    # --------------------------------------------------------
    # Queries
    # --------------------------------------------------------

    def all(
        self,
    ) -> List[ProviderConnection]:

        return list(self._connections.values())

    def workspace_connections(
        self,
        workspace_id: int,
    ) -> List[ProviderConnection]:

        return [

            connection

            for connection in self._connections.values()

            if connection.workspace_id == workspace_id

        ]

    # --------------------------------------------------------
    # Utilities
    # --------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._connections.clear()


# ============================================================
# Global Persistence
# ============================================================

memory_connection_persistence = MemoryConnectionPersistence()


# ============================================================
# Public Exports
# ============================================================

__all__ = [

    "MemoryConnectionPersistence",

    "memory_connection_persistence",

]