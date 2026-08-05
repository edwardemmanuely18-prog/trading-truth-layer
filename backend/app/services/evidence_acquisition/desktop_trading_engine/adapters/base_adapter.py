"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Desktop Trading Engine

Base Desktop Adapter
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


# ============================================================================
# Canonical Desktop Acquisition Contract
# ============================================================================


class DesktopAcquisitionContract:
    """
    Canonical acquisition contract returned by every desktop adapter.

    This contract is provider-neutral and represents the complete
    evidence surface acquired from a desktop trading platform.

    Every desktop adapter MUST return a dictionary with the following
    top-level keys.
    """

    REQUIRED_KEYS = {

        # Infrastructure
        "terminal",
        "user",
        "broker",
        "server",
        "account",

        # Financial
        "balance",
        "margin",
        "equity",
        "buying_power",

        # Market
        "symbols",
        "prices",

        # Trading
        "orders",
        "executions",
        "deals",
        "trades",
        "positions",
        "history",
        "activities",

        # Metadata
        "connector_name",
        "connector_version",
    }

    @classmethod
    def validate(
        cls,
        payload: Dict[str, Any],
    ) -> None:

        missing = cls.REQUIRED_KEYS - payload.keys()

        if missing:

            raise ValueError(

                "Desktop acquisition contract missing keys:\n"

                + "\n".join(sorted(missing))

            )


class BaseDesktopAdapter(ABC):
    """
    Base contract for all desktop trading platform adapters.

    Adapters are responsible only for interacting with native broker
    APIs and returning raw platform evidence.

    They must not perform translation, validation, verification or
    business logic.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the platform name."""
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_version(self) -> str:
        """Return the platform/API version."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the platform."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Terminate the connection."""
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        """Return True if connected."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Evidence Acquisition
    # ------------------------------------------------------------------

    @abstractmethod
    def acquire(self) -> Dict[str, Any]:
        """
        Acquire all desktop trading evidence.

        Every adapter MUST return the canonical Desktop Acquisition
        Contract.

        Provider-specific APIs must be normalized into this contract
        before returning.

        No provider-native objects should escape the adapter boundary.
        """

        raise NotImplementedError

    # ------------------------------------------------------------------
    # Context Manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "BaseDesktopAdapter":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.disconnect()


__all__ = [
    "DesktopAcquisitionContract",
    "BaseDesktopAdapter",
]