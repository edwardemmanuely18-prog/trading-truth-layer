"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Base Adapter

Institutional base adapter shared by every Financial
Infrastructure provider.

Concrete adapters should focus only on acquiring native
provider evidence.

Common lifecycle, diagnostics and synchronization behaviour
is implemented here.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..connectors import FinancialConnector
from ..provider import (
    ProviderCapability,
    ProviderDescriptor,
)


# ============================================================================
# Adapter Statistics
# ============================================================================


@dataclass(slots=True)
class AdapterStatistics:
    """
    Runtime adapter statistics.
    """

    acquisitions: int = 0

    acquired_objects: int = 0

    successful_syncs: int = 0

    failed_syncs: int = 0

    last_duration_ms: float = 0.0


# ============================================================================
# Adapter Diagnostics
# ============================================================================


@dataclass(slots=True)
class AdapterDiagnostics:
    """
    Runtime adapter diagnostics.
    """

    provider: str

    connected: bool

    authenticated: bool

    healthy: bool

    last_sync: Optional[datetime]

    statistics: AdapterStatistics


# ============================================================================
# Financial Adapter
# ============================================================================


class FinancialAdapter(ABC):
    """
    Institutional base adapter.

    Every Financial provider adapter inherits from this class.
    """

    def __init__(
        self,
        connector: FinancialConnector,
    ) -> None:

        self.connector = connector

        self.statistics = AdapterStatistics()

        self.last_sync: Optional[
            datetime
        ] = None

    # ------------------------------------------------------------------
    # Provider Metadata
    # ------------------------------------------------------------------

    @abstractmethod
    def descriptor(
        self,
    ) -> ProviderDescriptor:
        """
        Provider metadata.
        """

    @abstractmethod
    def capability(
        self,
    ) -> ProviderCapability:
        """
        Supported provider capabilities.
        """

    # ------------------------------------------------------------------
    # Acquisition
    # ------------------------------------------------------------------

    @abstractmethod
    def acquire(
        self,
    ) -> List[Any]:
        """
        Acquire native provider objects.
        """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:

        self.connector.connect()

    def authenticate(self) -> None:

        self.connector.authenticate()

    def disconnect(self) -> None:

        self.connector.disconnect()

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def connected(self) -> bool:

        return self.connector.connected

    def authenticated(self) -> bool:

        return self.connector.authenticated

    def healthy(self) -> bool:

        return self.connector.health_check()

    # ------------------------------------------------------------------
    # Synchronization Hooks
    # ------------------------------------------------------------------

    def begin_sync(self) -> datetime:

        self.statistics.acquisitions += 1

        return datetime.utcnow()

    def finish_sync(
        self,
        started_at: datetime,
        acquired: int,
        successful: bool,
    ) -> None:

        finished = datetime.utcnow()

        self.last_sync = finished

        self.statistics.acquired_objects += acquired

        duration = (
            finished - started_at
        ).total_seconds() * 1000

        self.statistics.last_duration_ms = duration

        if successful:

            self.statistics.successful_syncs += 1

        else:

            self.statistics.failed_syncs += 1

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> AdapterDiagnostics:

        return AdapterDiagnostics(

            provider=self.descriptor().name,

            connected=self.connected(),

            authenticated=self.authenticated(),

            healthy=self.healthy(),

            last_sync=self.last_sync,

            statistics=self.statistics,
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def reset_statistics(
        self,
    ) -> None:

        self.statistics = AdapterStatistics()

    def metadata(
        self,
    ) -> Dict[str, Any]:

        descriptor = self.descriptor()

        capability = self.capability()

        return {

            "provider": descriptor.name,

            "display_name": descriptor.display_name,

            "vendor": descriptor.vendor,

            "version": descriptor.version,

            "description": descriptor.description,

            "streaming": capability.streaming,

            "historical_sync": capability.historical_sync,

            "incremental_sync": capability.incremental_sync,

            "batch_sync": capability.batch_sync,

            "authentication": capability.authentication,
        }


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [
    "AdapterStatistics",
    "AdapterDiagnostics",
    "FinancialAdapter",
]