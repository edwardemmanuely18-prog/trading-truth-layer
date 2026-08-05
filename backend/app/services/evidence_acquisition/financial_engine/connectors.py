"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Connector Contracts

Institutional connector contracts shared by every Financial
Infrastructure provider.

Connectors manage provider connectivity only.

They are intentionally independent from adapters,
translators, synchronizers and registries.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from enum import Enum

from typing import Dict
from typing import List
from typing import Optional


# ============================================================================
# Connection State
# ============================================================================


class ConnectionState(str, Enum):
    """
    Financial provider connection lifecycle.
    """

    DISCONNECTED = "disconnected"

    CONNECTING = "connecting"

    CONNECTED = "connected"

    AUTHENTICATING = "authenticating"

    AUTHENTICATED = "authenticated"

    DEGRADED = "degraded"

    FAILED = "failed"


# ============================================================================
# Connector Configuration
# ============================================================================


@dataclass(slots=True)
class ConnectionConfiguration:
    """
    Connector configuration.
    """

    endpoint: str

    timeout_seconds: int = 30

    reconnect: bool = True

    verify_tls: bool = True

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


# ============================================================================
# Connection Information
# ============================================================================


@dataclass(slots=True)
class ConnectionInformation:
    """
    Runtime connection information.
    """

    provider: str

    state: ConnectionState = (
        ConnectionState.DISCONNECTED
    )

    connected_at: Optional[
        datetime
    ] = None

    authenticated_at: Optional[
        datetime
    ] = None

    latency_ms: Optional[
        float
    ] = None

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


# ============================================================================
# Connector Capability
# ============================================================================


@dataclass(slots=True)
class ConnectorCapability:
    """
    Supported connector capabilities.
    """

    streaming: bool = False

    incremental_sync: bool = True

    historical_sync: bool = True

    batch_sync: bool = True

    health_check: bool = True

    ping: bool = True

    reconnect: bool = True

    authentication: bool = True

    tls: bool = True


# ============================================================================
# Financial Connector
# ============================================================================


class FinancialConnector(ABC):
    """
    Base connector for every Financial provider.
    """

    def __init__(
        self,
        configuration: ConnectionConfiguration,
    ) -> None:

        self.configuration = configuration

        self.connection = ConnectionInformation(
            provider=self.provider_name()
        )

        self.capabilities = (
            ConnectorCapability()
        )

    @abstractmethod
    def provider_name(self) -> str:
        """
        Provider identifier.
        """

    @abstractmethod
    def connect(self) -> None:
        """
        Establish provider connection.
        """

    @abstractmethod
    def authenticate(self) -> None:
        """
        Authenticate provider session.
        """

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect provider.
        """

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check provider health.
        """

    @abstractmethod
    def ping(self) -> float:
        """
        Return provider latency.
        """

    @property
    def connected(self) -> bool:

        return (
            self.connection.state
            in (
                ConnectionState.CONNECTED,
                ConnectionState.AUTHENTICATED,
            )
        )

    @property
    def authenticated(self) -> bool:

        return (
            self.connection.state
            ==
            ConnectionState.AUTHENTICATED
        )


# ============================================================================
# Connector Registry
# ============================================================================


class ConnectorRegistry:
    """
    Registry of Financial connectors.
    """

    def __init__(self) -> None:

        self._connectors: Dict[
            str,
            FinancialConnector,
        ] = {}

    def register(
        self,
        connector: FinancialConnector,
    ) -> None:

        self._connectors[
            connector.provider_name()
        ] = connector

    def unregister(
        self,
        provider: str,
    ) -> None:

        self._connectors.pop(
            provider,
            None,
        )

    def connector(
        self,
        provider: str,
    ) -> Optional[
        FinancialConnector
    ]:

        return self._connectors.get(
            provider
        )

    def providers(self) -> List[str]:

        return sorted(
            self._connectors.keys()
        )

    def connectors(
        self,
    ) -> List[
        FinancialConnector
    ]:

        return list(
            self._connectors.values()
        )

    def count(self) -> int:

        return len(
            self._connectors
        )

    def clear(self) -> None:

        self._connectors.clear()


# ============================================================================
# Connector Diagnostics
# ============================================================================


@dataclass(slots=True)
class ConnectorDiagnostics:
    """
    Runtime connector diagnostics.
    """

    provider_count: int

    connected: int

    authenticated: int

    failed: int

    degraded: int


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "ConnectionState",

    "ConnectionConfiguration",

    "ConnectionInformation",

    "ConnectorCapability",

    "FinancialConnector",

    "ConnectorRegistry",

    "ConnectorDiagnostics",
]