"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Desktop Connector

Institutional bridge between Desktop Adapters and the
Universal Evidence Connector Framework.
"""

from __future__ import annotations

from typing import Any

from ..adapters.base_adapter import BaseDesktopAdapter
from ..connectors import BaseConnector, ConnectorConfiguration
from ..translators import BaseTranslator


class DesktopConnector(BaseConnector):
    """
    Canonical connector for every desktop trading platform.

    Responsibilities
    ----------------
    • Own a desktop adapter
    • Delegate lifecycle to the adapter
    • Acquire native platform evidence
    • Allow BaseConnector to perform translation

    This class intentionally contains no:

        • Provider-specific logic
        • Translation logic
        • Validation logic
        • Business rules
    """

    def __init__(
        self,
        *,
        adapter: BaseDesktopAdapter,
        configuration: ConnectorConfiguration,
        translator: BaseTranslator,
    ) -> None:
        super().__init__(
            configuration=configuration,
            translator=translator,
        )

        self.adapter = adapter

        self.provider_name = adapter.provider_name
        self.provider_version = adapter.provider_version

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        self.adapter.connect()
        self._connected = True

    def disconnect(self) -> None:
        self.adapter.disconnect()
        self._connected = False

    def is_connected(self) -> bool:
        return self.adapter.is_connected()

    # ------------------------------------------------------------------
    # Acquisition
    # ------------------------------------------------------------------

    def acquire(self) -> Any:
        """
        Acquire the native evidence payload from the
        underlying desktop adapter.

        Returns
        -------
        Provider-native acquisition payload.
        """
        return self.adapter.acquire()

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def adapter_name(self) -> str:
        return self.adapter.provider_name

    @property
    def adapter_version(self) -> str:
        return self.adapter.provider_version

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"provider={self.provider_name!r}, "
            f"version={self.provider_version!r})"
        )