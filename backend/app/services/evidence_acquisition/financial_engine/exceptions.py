"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Canonical Exceptions

These exceptions define the institutional error hierarchy used by the
Financial Infrastructure Engine. Every adapter, connector, translator,
validator, provider and synchronization component should raise
exceptions derived from FinancialEngineError.
"""

from __future__ import annotations


# ============================================================================
# Base Exception
# ============================================================================


class FinancialEngineError(Exception):
    """
    Base exception for every Financial Engine error.
    """

    pass


# ============================================================================
# Configuration
# ============================================================================


class FinancialConfigurationError(FinancialEngineError):
    """
    Invalid financial engine configuration.
    """

    pass


class ProviderRegistrationError(FinancialEngineError):
    """
    Raised when a provider cannot be registered.
    """

    pass


class ProviderNotFoundError(FinancialEngineError):
    """
    Requested provider does not exist.
    """

    pass


# ============================================================================
# Connection
# ============================================================================


class FinancialConnectionError(FinancialEngineError):
    """
    Unable to establish financial provider connection.
    """

    pass


class FinancialAuthenticationError(FinancialEngineError):
    """
    Financial provider authentication failed.
    """

    pass


class FinancialAuthorizationError(FinancialEngineError):
    """
    Financial provider authorization failed.
    """

    pass


class FinancialTimeoutError(FinancialEngineError):
    """
    Financial provider request timed out.
    """

    pass


class FinancialSessionError(FinancialEngineError):
    """
    Invalid financial provider session.
    """

    pass


# ============================================================================
# Synchronization
# ============================================================================


class SynchronizationError(FinancialEngineError):
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


class TranslationError(FinancialEngineError):
    """
    Native financial object translation failed.
    """

    pass


class UnsupportedEvidenceError(TranslationError):
    """
    Unsupported native evidence received.
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


class ValidationError(FinancialEngineError):
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


class InvalidCurrencyError(ValidationError):
    """
    Invalid currency detected.
    """

    pass


class InvalidInstitutionError(ValidationError):
    """
    Invalid financial institution.
    """

    pass


class InvalidAccountError(ValidationError):
    """
    Invalid financial account.
    """

    pass


class InvalidCounterpartyError(ValidationError):
    """
    Invalid counterparty.
    """

    pass


# ============================================================================
# Adapter
# ============================================================================


class AdapterError(FinancialEngineError):
    """
    Financial adapter error.
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


class ConnectorError(FinancialEngineError):
    """
    Financial connector error.
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


class ProviderError(FinancialEngineError):
    """
    Provider execution error.
    """

    pass


# ============================================================================
# Registry
# ============================================================================


class RegistryError(FinancialEngineError):
    """
    Financial registry error.
    """

    pass


class DuplicateEvidenceError(RegistryError):
    """
    Duplicate evidence detected.
    """

    pass


class RegistryWriteError(RegistryError):
    """
    Failed to write evidence into registry.
    """

    pass


class RegistryLookupError(RegistryError):
    """
    Failed to retrieve evidence from registry.
    """

    pass


# ============================================================================
# Provenance
# ============================================================================


class ProvenanceError(FinancialEngineError):
    """
    Evidence provenance error.
    """

    pass


class ProvenanceVerificationError(ProvenanceError):
    """
    Provenance verification failed.
    """

    pass


class ChecksumVerificationError(ProvenanceError):
    """
    Evidence checksum verification failed.
    """

    pass


# ============================================================================
# Publisher
# ============================================================================


class PublisherError(FinancialEngineError):
    """
    Financial publisher error.
    """

    pass


class PublicationError(PublisherError):
    """
    Evidence publication failed.
    """

    pass


class PublicationRejectedError(PublisherError):
    """
    Evidence publication rejected.
    """

    pass


# ============================================================================
# Engine
# ============================================================================


class EngineError(FinancialEngineError):
    """
    Financial engine error.
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
    "FinancialEngineError",

    # Configuration
    "FinancialConfigurationError",
    "ProviderRegistrationError",
    "ProviderNotFoundError",

    # Connection
    "FinancialConnectionError",
    "FinancialAuthenticationError",
    "FinancialAuthorizationError",
    "FinancialTimeoutError",
    "FinancialSessionError",

    # Synchronization
    "SynchronizationError",
    "SynchronizationCancelledError",
    "PartialSynchronizationError",

    # Translation
    "TranslationError",
    "UnsupportedEvidenceError",
    "MissingTranslatorError",

    # Validation
    "ValidationError",
    "InvalidEvidenceError",
    "MissingRequiredFieldError",
    "InvalidCurrencyError",
    "InvalidInstitutionError",
    "InvalidAccountError",
    "InvalidCounterpartyError",

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

    # Registry
    "RegistryError",
    "DuplicateEvidenceError",
    "RegistryWriteError",
    "RegistryLookupError",

    # Provenance
    "ProvenanceError",
    "ProvenanceVerificationError",
    "ChecksumVerificationError",

    # Publisher
    "PublisherError",
    "PublicationError",
    "PublicationRejectedError",

    # Engine
    "EngineError",
    "EngineNotStartedError",
    "EngineShutdownError",
]