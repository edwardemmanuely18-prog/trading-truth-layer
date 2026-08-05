"""
Trading Truth Layer (TTL)

Gateway Engine

Canonical Exceptions

These exceptions define the institutional error hierarchy used by the
Gateway Engine. Every adapter, connector, translator, validator,
provider and synchronization component should raise exceptions derived
from GatewayEngineError.
"""

from __future__ import annotations


# ============================================================================
# Base Exception
# ============================================================================


class GatewayEngineError(Exception):
    """
    Base exception for every Gateway Engine error.
    """

    pass


# ============================================================================
# Configuration
# ============================================================================


class GatewayConfigurationError(GatewayEngineError):
    """
    Invalid gateway configuration.
    """

    pass


class ProviderRegistrationError(GatewayEngineError):
    """
    Raised when a provider cannot be registered.
    """

    pass


class ProviderNotFoundError(GatewayEngineError):
    """
    Requested provider does not exist.
    """

    pass


# ============================================================================
# Connection
# ============================================================================


class GatewayConnectionError(GatewayEngineError):
    """
    Unable to establish gateway connection.
    """

    pass


class GatewayAuthenticationError(GatewayEngineError):
    """
    Gateway authentication failed.
    """

    pass


class GatewayAuthorizationError(GatewayEngineError):
    """
    Gateway authorization failed.
    """

    pass


class GatewayTimeoutError(GatewayEngineError):
    """
    Gateway request timed out.
    """

    pass


class GatewaySessionError(GatewayEngineError):
    """
    Invalid gateway session.
    """

    pass


# ============================================================================
# Synchronization
# ============================================================================


class SynchronizationError(GatewayEngineError):
    """
    Synchronization process failed.
    """

    pass


class SynchronizationCancelledError(SynchronizationError):
    """
    Synchronization cancelled.
    """

    pass


class PartialSynchronizationError(SynchronizationError):
    """
    Synchronization completed partially.
    """

    pass


# ============================================================================
# Translation
# ============================================================================


class TranslationError(GatewayEngineError):
    """
    Native gateway object translation failed.
    """

    pass


class UnsupportedObjectError(TranslationError):
    """
    Unsupported native object received.
    """

    pass


class MissingTranslatorError(TranslationError):
    """
    Translator not available.
    """

    pass


# ============================================================================
# Validation
# ============================================================================


class ValidationError(GatewayEngineError):
    """
    Canonical evidence validation failed.
    """

    pass


class InvalidEvidenceError(ValidationError):
    """
    Invalid canonical evidence object.
    """

    pass


class MissingRequiredFieldError(ValidationError):
    """
    Required evidence field missing.
    """

    pass


# ============================================================================
# Adapter
# ============================================================================


class AdapterError(GatewayEngineError):
    """
    Gateway adapter error.
    """

    pass


class AdapterNotInitializedError(AdapterError):
    """
    Adapter used before initialization.
    """

    pass


class AdapterClosedError(AdapterError):
    """
    Adapter has already been closed.
    """

    pass


class UnsupportedCapabilityError(AdapterError):
    """
    Adapter does not support requested capability.
    """

    pass


# ============================================================================
# Connector
# ============================================================================


class ConnectorError(GatewayEngineError):
    """
    Gateway connector error.
    """

    pass


class ConnectorStateError(ConnectorError):
    """
    Invalid connector state.
    """

    pass


# ============================================================================
# Provider
# ============================================================================


class ProviderError(GatewayEngineError):
    """
    Provider execution error.
    """

    pass


# ============================================================================
# Engine
# ============================================================================


class EngineError(GatewayEngineError):
    """
    Gateway engine error.
    """

    pass


class EngineNotStartedError(EngineError):
    """
    Engine operation requested before startup.
    """

    pass


class EngineShutdownError(EngineError):
    """
    Engine has already been shut down.
    """

    pass


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    # Base
    "GatewayEngineError",

    # Configuration
    "GatewayConfigurationError",
    "ProviderRegistrationError",
    "ProviderNotFoundError",

    # Connection
    "GatewayConnectionError",
    "GatewayAuthenticationError",
    "GatewayAuthorizationError",
    "GatewayTimeoutError",
    "GatewaySessionError",

    # Synchronization
    "SynchronizationError",
    "SynchronizationCancelledError",
    "PartialSynchronizationError",

    # Translation
    "TranslationError",
    "UnsupportedObjectError",
    "MissingTranslatorError",

    # Validation
    "ValidationError",
    "InvalidEvidenceError",
    "MissingRequiredFieldError",

    # Adapter
    "AdapterError",
    "AdapterNotInitializedError",
    "AdapterClosedError",
    "UnsupportedCapabilityError",

    # Connector
    "ConnectorError",
    "ConnectorStateError",

    # Provider
    "ProviderError",

    # Engine
    "EngineError",
    "EngineNotStartedError",
    "EngineShutdownError",
]