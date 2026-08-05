"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Canonical Exception Hierarchy

Every component of the Universal Evidence Adapter raises
exceptions defined in this module.

No provider-specific exceptions should exist here.
"""

from __future__ import annotations

from typing import Optional


# ============================================================================
# Base Exceptions
# ============================================================================


class UEAError(Exception):
    """
    Root exception for the Universal Evidence Adapter.

    Every UEA exception ultimately derives from this class.
    """

    def __init__(
        self,
        message: str,
        *,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)

        self.message = message

        self.cause = cause

    def __str__(self) -> str:
        return self.message


# ============================================================================
# Configuration
# ============================================================================


class ConfigurationError(UEAError):
    """
    Raised when a connector or component is improperly configured.
    """
    pass


# ============================================================================
# Validation
# ============================================================================


class ValidationError(UEAError):
    """
    Raised when canonical evidence fails validation.
    """
    pass


# ============================================================================
# Translation
# ============================================================================


class TranslationError(UEAError):
    """
    Raised when native provider objects cannot be translated
    into canonical evidence.
    """
    pass


# ============================================================================
# Runtime
# ============================================================================


class ConnectionError(UEAError):
    """
    Raised when a connection to a desktop trading platform
    cannot be established or maintained.
    """
    pass


class SynchronizationError(UEAError):
    """
    Raised when a synchronization cycle fails.
    """
    pass


# ============================================================================
# Provider
# ============================================================================


class ProviderError(UEAError):
    """
    Base exception for provider-specific runtime failures.

    Connectors should translate native provider exceptions
    into subclasses of this exception before exposing them
    to the rest of the UEA.
    """

    def __init__(
        self,
        message: str,
        *,
        provider: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message, cause=cause)

        self.provider = provider


class UnsupportedProviderError(ProviderError):
    """
    Raised when a provider is not registered or supported
    by the Universal Evidence Adapter.
    """

    def __init__(
        self,
        provider: str,
        *,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(
            f"Unsupported provider: {provider}",
            provider=provider,
            cause=cause,
        )


# ============================================================================
# Framework
# ============================================================================


class PackageError(UEAError):
    """
    Raised when an evidence package is incomplete,
    inconsistent, or otherwise invalid for processing.
    """
    pass


class RegistryError(UEAError):
    """
    Raised when interacting with the connector registry.

    Examples include duplicate registrations, missing
    providers, or registry initialization failures.
    """
    pass


class EngineError(UEAError):
    """
    Raised by the Universal Evidence Adapter engine.

    Represents unrecoverable orchestration failures that
    occur above individual connectors and synchronizers.
    """
    pass


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    # Base
    "UEAError",

    # Configuration
    "ConfigurationError",

    # Validation
    "ValidationError",

    # Translation
    "TranslationError",

    # Runtime
    "ConnectionError",
    "SynchronizationError",

    # Provider
    "ProviderError",
    "UnsupportedProviderError",

    # Framework
    "PackageError",
    "RegistryError",
    "EngineError",
]