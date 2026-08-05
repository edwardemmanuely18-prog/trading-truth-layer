"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Connector Framework
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Optional

from .exceptions import (
    ConfigurationError,
    ConnectionError,
)
from .models import DesktopEvidencePackage
from .translators import BaseTranslator, TranslationPipeline


# ============================================================================
# Connector Configuration
# ============================================================================


class ConnectorConfiguration:
    """
    Generic connector configuration.

    Provider-specific connectors may extend this class if
    additional configuration is required.
    """

    def __init__(
        self,
        *,
        provider: str,
        settings: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.provider = provider.lower()
        self.settings = settings or {}

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.settings.get(key, default)

    def require(
        self,
        key: str,
    ) -> Any:
        if key not in self.settings:
            raise ConfigurationError(
                f"Missing required configuration: '{key}'."
            )

        return self.settings[key]


# ============================================================================
# Base Connector
# ============================================================================


class BaseConnector(ABC):
    """
    Base class for all Desktop Trading Engine connectors.
    """

    provider_name: str = "unknown"

    provider_version: str = "unknown"

    def __init__(
        self,
        *,
        configuration: ConnectorConfiguration,
        translator: BaseTranslator,
    ) -> None:
        self.configuration = configuration
        self.translator = translator
        self.pipeline = TranslationPipeline(translator)

        self._connected = False

    # ---------------------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------------------

    @abstractmethod
    def connect(self) -> None:
        """
        Establish a connection to the provider.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the provider connection.
        """
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Return True if the connector is currently connected.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------
    # Acquisition
    # ---------------------------------------------------------------------

    @abstractmethod
    def acquire(self) -> Any:
        """
        Acquire native provider data.

        Returns provider-native payload.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------
    # Translation
    # ---------------------------------------------------------------------

    def synchronize(self) -> DesktopEvidencePackage:
        """
        Acquire native data and translate it into a
        DesktopEvidencePackage.
        """

        if not self.is_connected():
            raise ConnectionError(
                f"{self.provider_name} connector is not connected."
            )

        native_payload = self.acquire()

        return self.pipeline.run(native_payload)

    # ---------------------------------------------------------------------
    # Context Manager
    # ---------------------------------------------------------------------

    def __enter__(self):
        self.connect()
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        self.disconnect()


# ============================================================================
# Connector Factory
# ============================================================================


class ConnectorFactory:
    """
    Creates connector instances.

    Concrete implementations typically override this factory
    to construct provider-specific connectors.
    """

    @staticmethod
    def create(
        connector_type,
        *,
        configuration: ConnectorConfiguration,
        translator: BaseTranslator,
    ) -> BaseConnector:
        return connector_type(
            configuration=configuration,
            translator=translator,
        )


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "ConnectorConfiguration",
    "BaseConnector",
    "ConnectorFactory",
]