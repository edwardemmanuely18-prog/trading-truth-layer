"""
Trading Truth Layer (TTL)

Gateway Engine

Base Adapter

Defines the canonical acquisition contract implemented by every
Gateway adapter.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import Optional

from ..models import GatewayType


# ============================================================================
# Adapter State
# ============================================================================


class AdapterState(str, Enum):
    """
    Runtime adapter lifecycle.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    CONNECTED = "connected"

    DISCONNECTED = "disconnected"

    FAILED = "failed"

    CLOSED = "closed"


# ============================================================================
# Adapter Statistics
# ============================================================================


@dataclass(slots=True)
class AdapterStatistics:
    """
    Runtime adapter statistics.
    """

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    initialized_at: Optional[datetime] = None

    connected_at: Optional[datetime] = None

    disconnected_at: Optional[datetime] = None

    acquisitions: int = 0

    failures: int = 0

    last_error: Optional[str] = None


# ============================================================================
# Base Adapter
# ============================================================================


class BaseGatewayAdapter(ABC):
    """
    Canonical Gateway adapter contract.

    Adapters are responsible for acquiring normalized provider
    data. They do not perform evidence translation.
    """

    def __init__(
        self,
        *,
        provider_name: str,
        gateway_type: GatewayType,
    ) -> None:

        self.provider_name = provider_name

        self.gateway_type = gateway_type

        self.state = AdapterState.CREATED

        self.statistics = AdapterStatistics()


# ============================================================================
# Lifecycle
# ============================================================================


    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize provider resources.
        """
        raise NotImplementedError


    @abstractmethod
    def connect(self) -> None:
        """
        Establish a connection to the provider.
        """
        raise NotImplementedError


    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect from the provider.
        """
        raise NotImplementedError


    @abstractmethod
    def acquire(self) -> Dict[str, Any]:
        """
        Acquire provider data.

        Returns
        -------
        Dict[str, Any]

            Dictionary keyed by canonical evidence category
            (accounts, orders, positions, trades, etc.) whose
            values are normalized provider objects ready for the
            translation layer.
        """
        raise NotImplementedError


    @abstractmethod
    def close(self) -> None:
        """
        Release provider resources.
        """
        raise NotImplementedError


# ============================================================================
# State Management
# ============================================================================

    def mark_initialized(self) -> None:
        """
        Mark the adapter as initialized.
        """

        self.state = AdapterState.INITIALIZED

        self.statistics.initialized_at = (
            datetime.utcnow()
        )


    def mark_connected(self) -> None:
        """
        Mark the adapter as connected.
        """

        self.state = AdapterState.CONNECTED

        self.statistics.connected_at = (
            datetime.utcnow()
        )


    def mark_disconnected(self) -> None:
        """
        Mark the adapter as disconnected.
        """

        self.state = AdapterState.DISCONNECTED

        self.statistics.disconnected_at = (
            datetime.utcnow()
        )


    def mark_failed(
        self,
        error: Exception | str,
    ) -> None:
        """
        Record an adapter failure.
        """

        self.state = AdapterState.FAILED

        self.statistics.failures += 1

        self.statistics.last_error = str(error)


    def mark_closed(self) -> None:
        """
        Mark the adapter as closed.
        """

        self.state = AdapterState.CLOSED


    def record_acquisition(self) -> None:
        """
        Record a successful acquisition cycle.
        """

        self.statistics.acquisitions += 1


# ============================================================================
# Properties
# ============================================================================

    @property
    def is_initialized(self) -> bool:

        return self.state in (
            AdapterState.INITIALIZED,
            AdapterState.CONNECTED,
        )


    @property
    def is_connected(self) -> bool:

        return self.state == AdapterState.CONNECTED


    @property
    def is_closed(self) -> bool:

        return self.state == AdapterState.CLOSED


# ============================================================================
# Runtime Statistics
# ============================================================================

    @property
    def uptime(self):
        """
        Adapter uptime.
        """

        return (
            datetime.utcnow()
            - self.statistics.created_at
        )


    def statistics_summary(self) -> dict:
        """
        Runtime acquisition statistics.
        """

        return {

            "created_at":
                self.statistics.created_at,

            "initialized_at":
                self.statistics.initialized_at,

            "connected_at":
                self.statistics.connected_at,

            "disconnected_at":
                self.statistics.disconnected_at,

            "uptime_seconds":
                self.uptime.total_seconds(),

            "acquisitions":
                self.statistics.acquisitions,

            "failures":
                self.statistics.failures,

            "last_error":
                self.statistics.last_error,
        }


# ============================================================================
# Health
# ============================================================================

    def health(self) -> dict:
        """
        Adapter health.
        """

        return {

            "provider_name":
                self.provider_name,

            "gateway_type":
                self.gateway_type.value,

            "state":
                self.state.value,

            "connected":
                self.is_connected,

            "acquisitions":
                self.statistics.acquisitions,

            "failures":
                self.statistics.failures,
        }


# ============================================================================
# Capabilities
# ============================================================================

    def capabilities(self) -> dict:
        """
        Adapter capabilities.

        Concrete adapters may extend this method.
        """

        return {

            "provider_name":
                self.provider_name,

            "gateway_type":
                self.gateway_type.value,

            "streaming":
                False,

            "historical_data":
                False,

            "market_data":
                False,

            "orders":
                False,

            "positions":
                False,

            "trades":
                False,
        }


# ============================================================================
# Diagnostics
# ============================================================================

    def diagnostics(self) -> dict:
        """
        Complete adapter diagnostics.
        """

        return {

            "health":
                self.health(),

            "statistics":
                self.statistics_summary(),

            "capabilities":
                self.capabilities(),
        }


# ============================================================================
# Identity
# ============================================================================

    @property
    def adapter_name(self) -> str:
        """
        Runtime adapter class name.
        """

        return self.__class__.__name__


    @property
    def adapter_type(self) -> str:
        """
        Adapter type identifier.
        """

        return self.adapter_name


# ============================================================================
# Representation
# ============================================================================

    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"provider={self.provider_name!r}, "

            f"gateway_type={self.gateway_type.value!r}, "

            f"state={self.state.value!r})"

        )


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [

    "AdapterState",

    "AdapterStatistics",

    "BaseGatewayAdapter",
]