"""
Trading Truth Layer (TTL)

Gateway Engine

Provider Contracts

Defines the canonical provider interface implemented by every
Gateway provider.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from .gateway_connector import GatewayConnector
from .models import (
    GatewayEvidencePackage,
    GatewayType,
)
from .registry import ProviderDescriptor


# ============================================================================
# Provider State
# ============================================================================


class ProviderState(str, Enum):
    """
    Runtime provider lifecycle.
    """

    CREATED = "created"

    INITIALIZED = "initialized"

    READY = "ready"

    RUNNING = "running"

    STOPPED = "stopped"

    FAILED = "failed"


# ============================================================================
# Provider Statistics
# ============================================================================


@dataclass(slots=True)
class ProviderStatistics:
    """
    Runtime provider statistics.
    """

    created_at: datetime = datetime.utcnow()

    initialized_at: Optional[datetime] = None

    started_at: Optional[datetime] = None

    stopped_at: Optional[datetime] = None

    synchronizations: int = 0

    failures: int = 0

    last_error: Optional[str] = None


# ============================================================================
# Base Provider
# ============================================================================


class BaseGatewayProvider(ABC):
    """
    Base class implemented by every Gateway provider.
    """

    def __init__(
        self,
        descriptor: ProviderDescriptor,
        connector: GatewayConnector,
    ) -> None:

        self.descriptor = descriptor

        self.connector = connector

        self.state = ProviderState.CREATED

        self.statistics = ProviderStatistics()


# ============================================================================
# Identity
# ============================================================================


    @property
    def provider_name(self) -> str:

        return self.descriptor.provider_name

    @property
    def gateway_type(self) -> GatewayType:

        return self.descriptor.gateway_type

    @property
    def version(self) -> str:

        return self.descriptor.provider_version


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
    def start(self) -> None:
        """
        Start the provider.
        """
        raise NotImplementedError


    @abstractmethod
    def stop(self) -> None:
        """
        Stop the provider.
        """
        raise NotImplementedError


    @abstractmethod
    def synchronize(
        self,
    ) -> GatewayEvidencePackage:
        """
        Acquire canonical gateway evidence.
        """
        raise NotImplementedError


    @abstractmethod
    def close(self) -> None:
        """
        Release provider resources.
        """
        raise NotImplementedError


from dataclasses import field


# ============================================================================
# Provider Statistics
# ============================================================================


@dataclass(slots=True)
class ProviderStatistics:
    """
    Runtime provider statistics.
    """

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    initialized_at: Optional[datetime] = None

    started_at: Optional[datetime] = None

    stopped_at: Optional[datetime] = None

    synchronizations: int = 0

    failures: int = 0

    last_error: Optional[str] = None


# ============================================================================
# State Management
# ============================================================================


    def mark_initialized(self) -> None:

        self.state = ProviderState.INITIALIZED

        self.statistics.initialized_at = (
            datetime.utcnow()
        )

    def mark_ready(self) -> None:

        self.state = ProviderState.READY

    def mark_running(self) -> None:

        self.state = ProviderState.RUNNING

        self.statistics.started_at = (
            datetime.utcnow()
        )

    def mark_stopped(self) -> None:

        self.state = ProviderState.STOPPED

        self.statistics.stopped_at = (
            datetime.utcnow()
        )

    def mark_failed(
        self,
        error: Exception | str,
    ) -> None:

        self.state = ProviderState.FAILED

        self.statistics.failures += 1

        self.statistics.last_error = str(error)


# ============================================================================
# Connector Delegation
# ============================================================================


    def connect(self) -> None:
        """
        Connect using the configured connector.
        """

        self.connector.connect()

    def disconnect(self) -> None:
        """
        Disconnect using the configured connector.
        """

        self.connector.disconnect()


# ============================================================================
# Default Synchronization
# ============================================================================


    def synchronize(
        self,
    ) -> GatewayEvidencePackage:
        """
        Execute a synchronization cycle.

        Providers normally inherit this implementation.
        """

        try:

            package = (
                self.connector.synchronize()
            )

            self.statistics.synchronizations += 1

            return package

        except Exception as exc:

            self.mark_failed(exc)

            raise


# ============================================================================
# Status
# ============================================================================


    def status(self) -> dict:
        """
        Runtime provider status.
        """

        return {

            "provider_name":
                self.provider_name,

            "gateway_type":
                self.gateway_type.value,

            "version":
                self.version,

            "state":
                self.state.value,

            "connector":
                self.connector.status(),
        }


# ============================================================================
# Health
# ============================================================================


    def health(self) -> dict:
        """
        Provider health information.
        """

        return {

            "provider_name":
                self.provider_name,

            "state":
                self.state.value,

            "synchronizations":
                self.statistics.synchronizations,

            "failures":
                self.statistics.failures,

            "last_error":
                self.statistics.last_error,

            "connector":
                self.connector.health(),
        }


# ============================================================================
# Capabilities
# ============================================================================


    def capabilities(self) -> dict:
        """
        Provider capabilities.

        The descriptor represents static capabilities while
        the connector reports runtime capabilities.
        """

        return {

            "descriptor": {

                "provider_name":
                    self.descriptor.provider_name,

                "gateway_type":
                    self.descriptor.gateway_type.value,

                "provider_version":
                    self.descriptor.provider_version,

                "vendor":
                    self.descriptor.vendor,

                "supports_streaming":
                    self.descriptor.supports_streaming,

                "supports_historical_data":
                    self.descriptor.supports_historical_data,

                "supports_order_submission":
                    self.descriptor.supports_order_submission,

                "supports_positions":
                    self.descriptor.supports_positions,

                "supports_trades":
                    self.descriptor.supports_trades,

                "supports_market_data":
                    self.descriptor.supports_market_data,

                "supported_protocols":
                    list(
                        self.descriptor.supported_protocols
                    ),

                "supported_asset_classes":
                    list(
                        self.descriptor.supported_asset_classes
                    ),
            },

            "connector":
                self.connector.capabilities(),
        }


# ============================================================================
# Diagnostics
# ============================================================================

    def diagnostics(self) -> dict:
        """
        Complete provider diagnostics.
        """

        return {

            "provider": {

                "name":
                    self.provider_name,

                "gateway_type":
                    self.gateway_type.value,

                "version":
                    self.version,

                "state":
                    self.state.value,
            },

            "statistics": {

                "created_at":
                    self.statistics.created_at,

                "initialized_at":
                    self.statistics.initialized_at,

                "started_at":
                    self.statistics.started_at,

                "stopped_at":
                    self.statistics.stopped_at,

                "synchronizations":
                    self.statistics.synchronizations,

                "failures":
                    self.statistics.failures,

                "last_error":
                    self.statistics.last_error,
            },

            "descriptor": {

                "vendor":
                    self.descriptor.vendor,

                "description":
                    self.descriptor.description,

                "supports_streaming":
                    self.descriptor.supports_streaming,

                "supports_market_data":
                    self.descriptor.supports_market_data,

                "supports_positions":
                    self.descriptor.supports_positions,

                "supports_trades":
                    self.descriptor.supports_trades,

                "supports_order_submission":
                    self.descriptor.supports_order_submission,

                "supports_historical_data":
                    self.descriptor.supports_historical_data,

                "supported_protocols":
                    list(
                        self.descriptor.supported_protocols
                    ),

                "supported_asset_classes":
                    list(
                        self.descriptor.supported_asset_classes
                    ),
            },

            "connector":
                self.connector.diagnostics(),
        }


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

    "ProviderState",

    "ProviderStatistics",

    "BaseGatewayProvider",
]