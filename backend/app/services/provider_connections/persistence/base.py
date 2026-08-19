"""
Trading Truth Layer (TTL)

Provider Connections

Persistence Contract

Defines the canonical persistence interface for
Provider Connections.

Persistence implementations may store provider
connections in memory, databases, cloud storage,
or any future backend.

The Provider Connections Service depends only on
this contract.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from typing import List
from typing import Optional

from ..models import ProviderConnection


# ============================================================
# Base Persistence
# ============================================================


class BaseConnectionPersistence(ABC):
    """
    Canonical persistence contract for Provider Connections.
    """

    @abstractmethod
    def save(
        self,
        connection: ProviderConnection,
    ) -> None:
        """
        Persist a Provider Connection.
        """

    @abstractmethod
    def update(
        self,
        connection: ProviderConnection,
    ) -> None:
        """
        Update a persisted Provider Connection.
        """

    @abstractmethod
    def delete(
        self,
        connection_id: str,
    ) -> None:
        """
        Remove a Provider Connection.
        """

    @abstractmethod
    def get(
        self,
        connection_id: str,
    ) -> Optional[ProviderConnection]:
        """
        Retrieve a Provider Connection.
        """

    @abstractmethod
    def exists(
        self,
        connection_id: str,
    ) -> bool:
        """
        Determine whether a Provider Connection exists.
        """

    @abstractmethod
    def all(
        self,
    ) -> List[ProviderConnection]:
        """
        Return every Provider Connection.
        """

    @abstractmethod
    def workspace_connections(
        self,
        workspace_id: int,
    ) -> List[ProviderConnection]:
        """
        Return all Provider Connections for a workspace.
        """

    @abstractmethod
    def clear(
        self,
    ) -> None:
        """
        Remove all persisted connections.
        """