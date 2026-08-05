"""
Trading Truth Layer (TTL)

Gateway Engine

Connector Contracts

Defines the canonical connector interface used by every Gateway
connector implementation.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from .models import GatewayEvidencePackage


# ============================================================================
# Connector State
# ============================================================================


class ConnectorState(str, Enum):
    """
    Lifecycle state of a connector.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    CONNECTING = "connecting"

    CONNECTED = "connected"

    SYNCHRONIZING = "synchronizing"

    DISCONNECTED = "disconnected"

    CLOSED = "closed"

    FAILED = "failed"


# ============================================================================
# Connector Configuration
# ============================================================================


@dataclass(slots=True)
class ConnectorConfiguration:
    """
    Generic connector configuration.

    Provider-specific configuration should be supplied
    through the settings dictionary.
    """

    provider_name: str

    gateway_type: str

    timeout_seconds: int = 30

    reconnect_attempts: int = 3

    reconnect_delay_seconds: float = 5.0

    auto_reconnect: bool = True

    validate_evidence: bool = True

    translate_evidence: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    settings: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# Connector Statistics
# ============================================================================


@dataclass(slots=True)
class ConnectorStatistics:
    """
    Runtime connector statistics.
    """

    started_at: Optional[datetime] = None

    connected_at: Optional[datetime] = None

    disconnected_at: Optional[datetime] = None

    synchronizations: int = 0

    successful_synchronizations: int = 0

    failed_synchronizations: int = 0

    reconnects: int = 0

    last_error: Optional[str] = None


# ============================================================================
# Base Connector
# ============================================================================


class BaseGatewayConnector(ABC):
    """
    Abstract connector implemented by every Gateway connector.
    """

    def __init__(
        self,
        configuration: ConnectorConfiguration,
    ) -> None:

        self.configuration = configuration

        self.state = ConnectorState.CREATED

        self.statistics = ConnectorStatistics()

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize connector resources.
        """
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to the provider.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect from the provider.
        """
        raise NotImplementedError

    @abstractmethod
    def synchronize(
        self,
    ) -> GatewayEvidencePackage:
        """
        Synchronize canonical evidence.
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Release connector resources.
        """
        raise NotImplementedError


# ============================================================================
# Lifecycle Helpers
# ============================================================================

    @property
    def provider_name(self) -> str:
        """
        Registered provider name.
        """

        return self.configuration.provider_name

    @property
    def gateway_type(self) -> str:
        """
        Gateway technology.
        """

        return self.configuration.gateway_type

    @property
    def is_initialized(self) -> bool:

        return self.state in {

            ConnectorState.INITIALIZED,

            ConnectorState.CONNECTING,

            ConnectorState.CONNECTED,

            ConnectorState.SYNCHRONIZING,

        }

    @property
    def is_connected(self) -> bool:

        return self.state == ConnectorState.CONNECTED

    @property
    def is_synchronizing(self) -> bool:

        return self.state == ConnectorState.SYNCHRONIZING

    @property
    def is_closed(self) -> bool:

        return self.state == ConnectorState.CLOSED


# ============================================================================
# State Management
# ============================================================================

    def set_state(
        self,
        state: ConnectorState,
    ) -> None:
        """
        Update connector state.
        """

        self.state = state

    def mark_initialized(self) -> None:

        self.state = ConnectorState.INITIALIZED

    def mark_connecting(self) -> None:

        self.state = ConnectorState.CONNECTING

    def mark_connected(self) -> None:

        self.state = ConnectorState.CONNECTED

        self.statistics.connected_at = (
            datetime.utcnow()
        )

    def mark_synchronizing(self) -> None:

        self.state = ConnectorState.SYNCHRONIZING

    def mark_disconnected(self) -> None:

        self.state = ConnectorState.DISCONNECTED

        self.statistics.disconnected_at = (
            datetime.utcnow()
        )

    def mark_closed(self) -> None:

        self.state = ConnectorState.CLOSED

    def mark_failed(
        self,
        error: Exception | str,
    ) -> None:

        self.state = ConnectorState.FAILED

        self.statistics.last_error = str(error)


# ============================================================================
# Statistics Helpers
# ============================================================================

    def record_successful_sync(
        self,
    ) -> None:

        self.statistics.synchronizations += 1

        self.statistics.successful_synchronizations += 1

    def record_failed_sync(
        self,
        error: Exception | str,
    ) -> None:

        self.statistics.synchronizations += 1

        self.statistics.failed_synchronizations += 1

        self.statistics.last_error = str(error)

    def record_reconnect(
        self,
    ) -> None:

        self.statistics.reconnects += 1

    def reset_statistics(
        self,
    ) -> None:

        self.statistics = ConnectorStatistics(
            started_at=datetime.utcnow()
        )


# ============================================================================
# Introspection
# ============================================================================

    def status(self) -> Dict[str, Any]:
        """
        Connector runtime status.
        """

        return {

            "provider_name":
                self.provider_name,

            "gateway_type":
                self.gateway_type,

            "state":
                self.state.value,

            "statistics": {

                "started_at":
                    self.statistics.started_at,

                "connected_at":
                    self.statistics.connected_at,

                "disconnected_at":
                    self.statistics.disconnected_at,

                "synchronizations":
                    self.statistics.synchronizations,

                "successful_synchronizations":
                    self.statistics.successful_synchronizations,

                "failed_synchronizations":
                    self.statistics.failed_synchronizations,

                "reconnects":
                    self.statistics.reconnects,

                "last_error":
                    self.statistics.last_error,
            },
        }


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "ConnectorState",

    "ConnectorConfiguration",

    "ConnectorStatistics",

    "BaseGatewayConnector",
]