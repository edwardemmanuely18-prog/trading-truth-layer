"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Desktop Trading Engine

Canonical Desktop Connector
"""

from __future__ import annotations

from typing import Any

from .adapters.base_adapter import BaseDesktopAdapter
from .connectors import (
    BaseConnector,
    ConnectorConfiguration,
)
from .translators import BaseTranslator


class DesktopConnector(BaseConnector):
    """
    Universal connector for every supported desktop trading platform.

    A DesktopConnector is composed of:

        • Adapter
        • Translator
        • Configuration

    making it capable of synchronizing any supported broker
    without requiring provider-specific connector classes.

    Responsibilities
    ----------------

    • Manage adapter lifecycle
    • Acquire native platform evidence
    • Delegate translation to BaseConnector

    Never performs:

    • Translation
    • Validation
    • Verification
    • Business logic
    """

    def __init__(
        self,
        *,
        adapter: BaseDesktopAdapter,
        translator: BaseTranslator,
        configuration: ConnectorConfiguration,
    ) -> None:

        super().__init__(
            configuration=configuration,
            translator=translator,
        )

        self.adapter = adapter

        self.provider_name = adapter.provider_name
        self.provider_version = adapter.provider_version

    # ==============================================================
    # Lifecycle
    # ==============================================================

    def connect(self) -> None:
        self.adapter.connect()
        self._connected = True

    def disconnect(self) -> None:
        self.adapter.disconnect()
        self._connected = False

    def is_connected(self) -> bool:
        return self.adapter.is_connected()

    # ==============================================================
    # Acquisition
    # ==============================================================

    def acquire(self) -> Any:
        """
        Acquire native provider evidence.

        The adapter returns the canonical acquisition payload.
        BaseConnector subsequently performs translation.
        """

        return self.adapter.acquire()

    # ==============================================================
    # Convenience
    # ==============================================================

    @property
    def connected(self) -> bool:
        return self.is_connected()

    @property
    def adapter_name(self) -> str:
        return self.adapter.provider_name

    @property
    def adapter_version(self) -> str:
        return self.adapter.provider_version

    def reconnect(self) -> None:
        self.disconnect()
        self.connect()

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"provider={self.provider_name!r}, "
            f"version={self.provider_version!r})"
        )