"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Provider Contracts

Institutional provider abstractions for the Financial
Infrastructure Engine.

Providers are responsible only for acquiring native financial
objects from external infrastructure.

Providers do not perform translation, validation,
registration or synchronization.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from dataclasses import dataclass
from dataclasses import field

from typing import Dict
from typing import List
from typing import Optional

from .connectors import FinancialConnector


# ============================================================================
# Provider Descriptor
# ============================================================================


@dataclass(slots=True)
class ProviderDescriptor:
    """
    Describes a Financial provider.
    """

    name: str

    display_name: str

    version: str

    description: str

    vendor: str


# ============================================================================
# Provider Capability
# ============================================================================


@dataclass(slots=True)
class ProviderCapability:
    """
    Supported provider capabilities.
    """

    streaming: bool = False

    historical_sync: bool = True

    incremental_sync: bool = True

    batch_sync: bool = True

    health_check: bool = True

    authentication: bool = True

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


# ============================================================================
# Financial Provider
# ============================================================================


class FinancialProvider(ABC):
    """
    Base Financial provider.
    """

    def __init__(
        self,
        connector: FinancialConnector,
    ) -> None:

        self.connector = connector

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

    @abstractmethod
    def acquire(
        self,
    ) -> List[object]:
        """
        Acquire native provider objects.
        """

    def name(self) -> str:

        return self.descriptor().name

    def provider(self) -> str:

        return self.descriptor().name

    def connected(self) -> bool:

        return self.connector.connected

    def authenticated(self) -> bool:

        return self.connector.authenticated

    def health(self) -> bool:

        return self.connector.health_check()


# ============================================================================
# Provider Registry
# ============================================================================


class FinancialProviderRegistry:
    """
    Registry of Financial providers.
    """

    def __init__(self) -> None:

        self._providers: Dict[
            str,
            FinancialProvider,
        ] = {}

    def register(
        self,
        provider: FinancialProvider,
    ) -> None:

        self._providers[
            provider.name()
        ] = provider

    def unregister(
        self,
        name: str,
    ) -> None:

        self._providers.pop(
            name,
            None,
        )

    def provider(
        self,
        name: str,
    ) -> Optional[
        FinancialProvider
    ]:

        return self._providers.get(
            name
        )

    def providers(
        self,
    ) -> List[
        FinancialProvider
    ]:

        return list(
            self._providers.values()
        )

    def names(
        self,
    ) -> List[str]:

        return sorted(
            self._providers.keys()
        )

    def count(self) -> int:

        return len(
            self._providers
        )

    def clear(self) -> None:

        self._providers.clear()


# ============================================================================
# Provider Service
# ============================================================================


class ProviderService:
    """
    Canonical entry point for provider operations.
    """

    def __init__(
        self,
        registry: Optional[
            FinancialProviderRegistry
        ] = None,
    ) -> None:

        self.registry = (
            registry
            or FinancialProviderRegistry()
        )

    def register(
        self,
        provider: FinancialProvider,
    ) -> None:

        self.registry.register(
            provider
        )

    def unregister(
        self,
        name: str,
    ) -> None:

        self.registry.unregister(
            name
        )

    def provider(
        self,
        name: str,
    ) -> Optional[
        FinancialProvider
    ]:

        return self.registry.provider(
            name
        )

    def providers(
        self,
    ) -> List[
        FinancialProvider
    ]:

        return self.registry.providers()

    def count(self) -> int:

        return self.registry.count()

    def clear(self) -> None:

        self.registry.clear()


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [
    "ProviderDescriptor",
    "ProviderCapability",
    "FinancialProvider",
    "FinancialProviderRegistry",
    "ProviderService",
]