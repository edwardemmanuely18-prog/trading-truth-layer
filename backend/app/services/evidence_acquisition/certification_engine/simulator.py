"""
Canonical simulation contract for the Evidence Acquisition
Certification Engine (ICE).

Simulators emulate external providers so that acquisition engines
can be certified without requiring live accounts.

Every simulator implements the same synchronization contract,
allowing the Certification Engine to execute identical workflows
regardless of provider or acquisition engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ProviderSimulator(ABC):
    """
    Canonical simulator contract.

    A simulator represents an external provider during
    certification.

    It does not perform certification itself.

    It only emulates provider behaviour.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Canonical provider name.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """
        Acquisition engine supported by this simulator.
        """
        raise NotImplementedError

    @abstractmethod
    def authenticate(
        self,
        credentials: Dict[str, Any],
    ) -> bool:
        """
        Simulate provider authentication.
        """
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> bool:
        """
        Simulate provider connection.
        """
        raise NotImplementedError

    @abstractmethod
    def synchronize(self) -> Any:
        """
        Produce simulated provider evidence.

        Returned evidence should resemble the
        provider's production payload.
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """
        Simulate connection shutdown.
        """
        raise NotImplementedError

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Return simulator health information.
        """
        raise NotImplementedError


class BaseProviderSimulator(ProviderSimulator):
    """
    Base implementation shared by all provider simulators.
    """

    def __init__(self) -> None:
        self._connected: bool = False

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def health(self) -> Dict[str, Any]:
        return {
            "connected": self._connected,
            "provider": self.provider_name,
            "engine": self.engine_name,
        }


__all__ = [
    "ProviderSimulator",
    "BaseProviderSimulator",
]