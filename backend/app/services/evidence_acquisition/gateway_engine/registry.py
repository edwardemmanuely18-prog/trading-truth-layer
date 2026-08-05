"""
Trading Truth Layer (TTL)

Gateway Engine

Provider Registry

Institutional registry responsible for provider discovery,
registration and capability lookup.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from .exceptions import (
    ProviderNotFoundError,
    ProviderRegistrationError,
)
from .models import GatewayType


# ============================================================================
# Provider Descriptor
# ============================================================================


@dataclass(slots=True)
class ProviderDescriptor:
    """
    Immutable metadata describing a Gateway provider.
    """

    provider_name: str

    gateway_type: GatewayType

    provider_version: str = "1.0"

    vendor: Optional[str] = None

    description: Optional[str] = None

    supports_streaming: bool = False

    supports_historical_data: bool = False

    supports_order_submission: bool = False

    supports_positions: bool = False

    supports_trades: bool = False

    supports_market_data: bool = False

    supports_account_information: bool = False

    supports_multi_account: bool = False

    supports_reconnection: bool = True

    supported_protocols: List[str] = field(
        default_factory=list
    )

    supported_asset_classes: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


# ============================================================================
# Registry Entry
# ============================================================================


@dataclass(slots=True)
class RegistryEntry:
    """
    Couples a provider descriptor with its runtime instance.
    """

    descriptor: ProviderDescriptor

    provider: object


# ============================================================================
# Gateway Provider Registry
# ============================================================================


class GatewayProviderRegistry:
    """
    Central registry of Gateway providers.
    """

    def __init__(self) -> None:

        self._providers: Dict[
            str,
            RegistryEntry,
        ] = {}

    def register(
        self,
        descriptor: ProviderDescriptor,
        provider: object,
    ) -> None:
        """
        Register a Gateway provider.
        """

        name = descriptor.provider_name

        if name in self._providers:

            raise ProviderRegistrationError(
                f"Provider '{name}' is already registered."
            )

        self._providers[name] = RegistryEntry(
            descriptor=descriptor,
            provider=provider,
        )

    def unregister(
        self,
        provider_name: str,
    ) -> None:
        """
        Remove a provider from the registry.
        """

        self._providers.pop(
            provider_name,
            None,
        )

    def clear(self) -> None:
        """
        Remove all providers.
        """

        self._providers.clear()

    def exists(
        self,
        provider_name: str,
    ) -> bool:
        """
        Determine whether a provider is registered.
        """

        return provider_name in self._providers

    def count(self) -> int:
        """
        Number of registered providers.
        """

        return len(self._providers)


# ============================================================================
# Provider Retrieval
# ============================================================================

    def get(
        self,
        provider_name: str,
    ) -> object:
        """
        Retrieve a registered provider instance.
        """

        entry = self._providers.get(
            provider_name
        )

        if entry is None:

            raise ProviderNotFoundError(
                f"Provider '{provider_name}' is not registered."
            )

        return entry.provider

    def descriptor(
        self,
        provider_name: str,
    ) -> ProviderDescriptor:
        """
        Retrieve provider descriptor.
        """

        entry = self._providers.get(
            provider_name
        )

        if entry is None:

            raise ProviderNotFoundError(
                f"Provider '{provider_name}' is not registered."
            )

        return entry.descriptor

    def entry(
        self,
        provider_name: str,
    ) -> RegistryEntry:
        """
        Retrieve the complete registry entry.
        """

        entry = self._providers.get(
            provider_name
        )

        if entry is None:

            raise ProviderNotFoundError(
                f"Provider '{provider_name}' is not registered."
            )

        return entry


# ============================================================================
# Enumeration
# ============================================================================

    def provider_names(
        self,
    ) -> List[str]:
        """
        Return registered provider names.
        """

        return sorted(
            self._providers.keys()
        )

    def descriptors(
        self,
    ) -> List[ProviderDescriptor]:
        """
        Return every registered descriptor.
        """

        return [

            entry.descriptor

            for entry in self._providers.values()

        ]

    def providers(
        self,
    ) -> List[object]:
        """
        Return provider instances.
        """

        return [

            entry.provider

            for entry in self._providers.values()

        ]

    def entries(
        self,
    ) -> List[RegistryEntry]:
        """
        Return registry entries.
        """

        return list(
            self._providers.values()
        )


# ============================================================================
# Gateway Type Discovery
# ============================================================================

    def by_gateway_type(
        self,
        gateway_type: GatewayType,
    ) -> List[RegistryEntry]:
        """
        Find providers implementing a gateway type.
        """

        return [

            entry

            for entry in self._providers.values()

            if entry.descriptor.gateway_type
            == gateway_type

        ]


# ============================================================================
# Capability Discovery
# ============================================================================

    def supports_streaming(
        self,
    ) -> List[RegistryEntry]:

        return [

            entry

            for entry in self._providers.values()

            if entry.descriptor.supports_streaming

        ]

    def supports_market_data(
        self,
    ) -> List[RegistryEntry]:

        return [

            entry

            for entry in self._providers.values()

            if entry.descriptor.supports_market_data

        ]

    def supports_order_submission(
        self,
    ) -> List[RegistryEntry]:

        return [

            entry

            for entry in self._providers.values()

            if entry.descriptor.supports_order_submission

        ]

    def supports_positions(
        self,
    ) -> List[RegistryEntry]:

        return [

            entry

            for entry in self._providers.values()

            if entry.descriptor.supports_positions

        ]

    def supports_trades(
        self,
    ) -> List[RegistryEntry]:

        return [

            entry

            for entry in self._providers.values()

            if entry.descriptor.supports_trades

        ]

    def supports_historical_data(
        self,
    ) -> List[RegistryEntry]:

        return [

            entry

            for entry in self._providers.values()

            if entry.descriptor.supports_historical_data

        ]

    def supports_multi_account(
        self,
    ) -> List[RegistryEntry]:

        return [

            entry

            for entry in self._providers.values()

            if entry.descriptor.supports_multi_account

        ]


# ============================================================================
# Protocol Discovery
# ============================================================================

    def protocol(
        self,
        protocol: str,
    ) -> List[RegistryEntry]:
        """
        Find providers supporting a protocol.
        """

        protocol = protocol.lower()

        return [

            entry

            for entry in self._providers.values()

            if any(

                p.lower() == protocol

                for p in entry.descriptor.supported_protocols

            )

        ]


# ============================================================================
# Asset Class Discovery
# ============================================================================

    def asset_class(
        self,
        asset_class: str,
    ) -> List[RegistryEntry]:
        """
        Find providers supporting an asset class.
        """

        asset_class = asset_class.lower()

        return [

            entry

            for entry in self._providers.values()

            if any(

                cls.lower() == asset_class

                for cls in entry.descriptor.supported_asset_classes

            )

        ]


# ============================================================================
# Introspection
# ============================================================================

    def statistics(
        self,
    ) -> Dict[str, object]:
        """
        Return registry statistics.
        """

        gateway_types = {}

        for entry in self._providers.values():

            gateway_type = (
                entry.descriptor.gateway_type.value
            )

            gateway_types.setdefault(
                gateway_type,
                0,
            )

            gateway_types[gateway_type] += 1

        return {

            "registered_providers": len(
                self._providers
            ),

            "gateway_types": gateway_types,

            "streaming_providers": len(
                self.supports_streaming()
            ),

            "market_data_providers": len(
                self.supports_market_data()
            ),

            "order_providers": len(
                self.supports_order_submission()
            ),

            "trade_providers": len(
                self.supports_trades()
            ),

            "position_providers": len(
                self.supports_positions()
            ),

            "historical_data_providers": len(
                self.supports_historical_data()
            ),

            "multi_account_providers": len(
                self.supports_multi_account()
            ),
        }


# ============================================================================
# Serialization
# ============================================================================

    def to_dict(
        self,
    ) -> Dict[str, Dict]:
        """
        Serialize provider descriptors.

        Runtime provider instances are intentionally excluded.
        """

        providers = {}

        for entry in self._providers.values():

            descriptor = entry.descriptor

            providers[
                descriptor.provider_name
            ] = {

                "provider_name":
                    descriptor.provider_name,

                "gateway_type":
                    descriptor.gateway_type.value,

                "provider_version":
                    descriptor.provider_version,

                "vendor":
                    descriptor.vendor,

                "description":
                    descriptor.description,

                "supports_streaming":
                    descriptor.supports_streaming,

                "supports_historical_data":
                    descriptor.supports_historical_data,

                "supports_order_submission":
                    descriptor.supports_order_submission,

                "supports_positions":
                    descriptor.supports_positions,

                "supports_trades":
                    descriptor.supports_trades,

                "supports_market_data":
                    descriptor.supports_market_data,

                "supports_account_information":
                    descriptor.supports_account_information,

                "supports_multi_account":
                    descriptor.supports_multi_account,

                "supports_reconnection":
                    descriptor.supports_reconnection,

                "supported_protocols":
                    list(
                        descriptor.supported_protocols
                    ),

                "supported_asset_classes":
                    list(
                        descriptor.supported_asset_classes
                    ),

                "metadata":
                    dict(
                        descriptor.metadata
                    ),
            }

        return providers


# ============================================================================
# Factory
# ============================================================================


def create_provider_registry(
) -> GatewayProviderRegistry:
    """
    Create an empty Gateway provider registry.
    """

    return GatewayProviderRegistry()


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "ProviderDescriptor",

    "RegistryEntry",

    "GatewayProviderRegistry",

    "create_provider_registry",
]