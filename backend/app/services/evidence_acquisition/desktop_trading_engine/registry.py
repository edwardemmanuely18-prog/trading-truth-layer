"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Registry Framework
"""

from __future__ import annotations

from typing import Dict
from typing import List
from typing import Optional

from .exceptions import RegistryError
from .translators import BaseTranslator


# ============================================================================
# Provider Registration
# ============================================================================


class ProviderDescriptor:
    """
    Describes a registered provider.
    """

    def __init__(
        self,
        *,
        name: str,
        version: str,
        translator: BaseTranslator,
        description: Optional[str] = None,
    ) -> None:
        self.name = name.lower()

        self.version = version

        self.description = description

        self.translator = translator

    def __repr__(self) -> str:
        return (
            f"ProviderDescriptor("
            f"name={self.name!r}, "
            f"version={self.version!r})"
        )


# ============================================================================
# Registry
# ============================================================================


class ProviderRegistry:
    """
    Canonical registry for Desktop Trading Engine providers.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, ProviderDescriptor] = {}

    # ---------------------------------------------------------------------
    # Registration
    # ---------------------------------------------------------------------

    def register(
        self,
        descriptor: ProviderDescriptor,
    ) -> None:
        """
        Register a provider.
        """

        provider = descriptor.name

        if provider in self._providers:
            raise RegistryError(
                f"Provider '{provider}' is already registered."
            )

        self._providers[provider] = descriptor

    def unregister(
        self,
        provider: str,
    ) -> None:
        """
        Remove a provider.
        """

        provider = provider.lower()

        if provider not in self._providers:
            raise RegistryError(
                f"Provider '{provider}' is not registered."
            )

        del self._providers[provider]

    # ---------------------------------------------------------------------
    # Lookup
    # ---------------------------------------------------------------------

    def get(
        self,
        provider: str,
    ) -> ProviderDescriptor:
        """
        Retrieve a provider descriptor.
        """

        provider = provider.lower()

        try:
            return self._providers[provider]

        except KeyError as exc:
            raise RegistryError(
                f"Unknown provider '{provider}'."
            ) from exc

    def translator(
        self,
        provider: str,
    ) -> BaseTranslator:
        """
        Retrieve a provider translator.
        """

        return self.get(provider).translator

    # ---------------------------------------------------------------------
    # Discovery
    # ---------------------------------------------------------------------

    def exists(
        self,
        provider: str,
    ) -> bool:
        """
        Determine whether a provider exists.
        """

        return provider.lower() in self._providers

    def providers(
        self,
    ) -> List[str]:
        """
        Return registered provider names.
        """

        return sorted(self._providers.keys())

    def descriptors(
        self,
    ) -> List[ProviderDescriptor]:
        """
        Return provider descriptors.
        """

        return list(self._providers.values())

    def clear(
        self,
    ) -> None:
        """
        Remove all providers.
        """

        self._providers.clear()

    def __len__(
        self,
    ) -> int:
        return len(self._providers)

    def __contains__(
        self,
        provider: str,
    ) -> bool:
        return provider.lower() in self._providers


# ============================================================================
# Global Registry
# ============================================================================

provider_registry = ProviderRegistry()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "ProviderDescriptor",
    "ProviderRegistry",
    "provider_registry",
]