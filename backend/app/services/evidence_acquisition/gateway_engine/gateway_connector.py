"""
Trading Truth Layer (TTL)

Gateway Engine

Gateway Connector

Institutional orchestration component responsible for coordinating
Gateway adapters, translators, validators and synchronizers.

The connector contains no provider-specific implementation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from .connectors import (
    BaseGatewayConnector,
    ConnectorConfiguration,
)
from .exceptions import (
    AdapterError,
    ConnectorError,
)
from .models import (
    GatewayEvidencePackage,
)
from .translators import (
    GatewayTranslatorManager,
    create_translation_manager,
)
from .validators import (
    GatewayEvidencePackageValidator,
)


# ============================================================================
# Gateway Connector
# ============================================================================


class GatewayConnector(BaseGatewayConnector):
    """
    Institutional Gateway connector.

    Coordinates:

    • Gateway Adapter
    • Translator Manager
    • Validator
    • Synchronizer

    while remaining completely provider-independent.
    """

    def __init__(
        self,
        configuration: ConnectorConfiguration,
        *,
        adapter,
        synchronizer,
        translator_manager: Optional[
            GatewayTranslatorManager
        ] = None,
        validator: Optional[
            GatewayEvidencePackageValidator
        ] = None,
    ) -> None:

        super().__init__(configuration)

        self.adapter = adapter

        self.synchronizer = synchronizer

        self.translator_manager = (
            translator_manager
            or create_translation_manager()
        )

        self.validator = (
            validator
            or GatewayEvidencePackageValidator()
        )

        self.created_at = datetime.utcnow()

        self.initialized = False


# ============================================================================
# Initialization
# ============================================================================


    def initialize(self) -> None:
        """
        Initialize connector dependencies.
        """

        if self.initialized:

            return

        if hasattr(
            self.adapter,
            "initialize",
        ):

            self.adapter.initialize()

        if hasattr(
            self.synchronizer,
            "initialize",
        ):

            self.synchronizer.initialize()

        self.mark_initialized()

        self.initialized = True


# ============================================================================
# Connection
# ============================================================================


    def connect(self) -> None:
        """
        Establish connection to the Gateway provider.
        """

        if not self.initialized:

            self.initialize()

        self.mark_connecting()

        try:

            self.adapter.connect()

        except Exception as exc:

            self.mark_failed(exc)

            raise AdapterError(
                str(exc)
            ) from exc

        self.mark_connected()


# ============================================================================
# Disconnection
# ============================================================================


    def disconnect(self) -> None:
        """
        Disconnect from provider.
        """

        try:

            self.adapter.disconnect()

        finally:

            self.mark_disconnected()


# ============================================================================
# Synchronization
# ============================================================================

    def synchronize(
        self,
    ) -> GatewayEvidencePackage:
        """
        Execute a complete synchronization cycle.

        Pipeline:

            Adapter
                ↓
            Synchronizer
                ↓
            Translator
                ↓
            Validator
                ↓
            GatewayEvidencePackage
        """

        if not self.is_connected:

            self.connect()

        self.mark_synchronizing()

        try:

            package = self.synchronizer.synchronize(

                adapter=self.adapter,

                translator_manager=self.translator_manager,

            )

            if self.configuration.validate_evidence:

                validation = self.validator.validate(
                    package
                )

                validation.raise_if_invalid()

            self.record_successful_sync()

            self.mark_connected()

            return package

        except Exception as exc:

            self.record_failed_sync(exc)

            self.mark_failed(exc)

            raise ConnectorError(
                f"Synchronization failed: {exc}"
            ) from exc


# ============================================================================
# Health
# ============================================================================

    def health(self) -> dict:
        """
        Connector health information.
        """

        return {

            "provider_name":
                self.provider_name,

            "gateway_type":
                self.gateway_type,

            "state":
                self.state.value,

            "initialized":
                self.initialized,

            "connected":
                self.is_connected,

            "synchronizations":
                self.statistics.synchronizations,

            "successful":
                self.statistics.successful_synchronizations,

            "failed":
                self.statistics.failed_synchronizations,

            "last_error":
                self.statistics.last_error,
        }


# ============================================================================
# Availability
# ============================================================================

    def ping(self) -> bool:
        """
        Verify provider availability.
        """

        if hasattr(
            self.adapter,
            "ping",
        ):

            return bool(
                self.adapter.ping()
            )

        return self.is_connected


# ============================================================================
# Reset
# ============================================================================

    def reset(self) -> None:
        """
        Reset connector runtime state.
        """

        self.reset_statistics()

        self.initialized = False

        self.mark_initialized()


# ============================================================================
# Shutdown
# ============================================================================

    def close(self) -> None:
        """
        Release connector resources.
        """

        try:

            if hasattr(
                self.adapter,
                "close",
            ):

                self.adapter.close()

        finally:

            if hasattr(
                self.synchronizer,
                "close",
            ):

                self.synchronizer.close()

            self.mark_closed()


# ============================================================================
# Dependency Introspection
# ============================================================================

    @property
    def adapter_name(self) -> str:
        """
        Runtime adapter class name.
        """

        return self.adapter.__class__.__name__

    @property
    def synchronizer_name(self) -> str:
        """
        Runtime synchronizer class name.
        """

        return self.synchronizer.__class__.__name__

    @property
    def validator_name(self) -> str:
        """
        Runtime validator class name.
        """

        return self.validator.__class__.__name__

    @property
    def translator_manager_name(self) -> str:
        """
        Runtime translator manager class name.
        """

        return (
            self.translator_manager.__class__.__name__
        )


# ============================================================================
# Capabilities
# ============================================================================

    def capabilities(self) -> dict:
        """
        Return connector capabilities.

        Provider-specific capabilities are exposed by the
        adapter. Connector-level capabilities are reported
        here.
        """

        adapter_capabilities = {}

        if hasattr(
            self.adapter,
            "capabilities",
        ):

            adapter_capabilities = (
                self.adapter.capabilities()
            )

        return {

            "provider_name":
                self.provider_name,

            "gateway_type":
                self.gateway_type,

            "translation_enabled":
                self.configuration.translate_evidence,

            "validation_enabled":
                self.configuration.validate_evidence,

            "auto_reconnect":
                self.configuration.auto_reconnect,

            "adapter":
                adapter_capabilities,
        }


# ============================================================================
# Diagnostics
# ============================================================================

    def diagnostics(self) -> dict:
        """
        Complete runtime diagnostics.
        """

        return {

            "status":
                self.status(),

            "health":
                self.health(),

            "capabilities":
                self.capabilities(),

            "dependencies": {

                "adapter":
                    self.adapter_name,

                "translator_manager":
                    self.translator_manager_name,

                "validator":
                    self.validator_name,

                "synchronizer":
                    self.synchronizer_name,
            },
        }


# ============================================================================
# Representation
# ============================================================================

    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"provider={self.provider_name!r}, "

            f"gateway_type={self.gateway_type!r}, "

            f"state={self.state.value!r})"

        )


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "GatewayConnector",
]