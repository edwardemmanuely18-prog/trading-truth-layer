"""
Canonical Acquisition Engine Contract.

Every Evidence Acquisition engine must implement this interface.

Examples
--------
- DesktopTradingEngine
- FinancialEngine
- GatewayEngine
- ExchangeEngine (future)
- DocumentEngine (future)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class AcquisitionEngine(ABC):
    """
    Canonical interface for Evidence Acquisition engines.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Engine name.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        """
        Engine version.
        """
        raise NotImplementedError

    @abstractmethod
    def initialize(self) -> None:
        """
        Prepare the engine for execution.
        """
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        """
        Start engine operations.
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """
        Stop engine operations gracefully.
        """
        raise NotImplementedError

    @abstractmethod
    def restart(self) -> None:
        """
        Restart the engine.
        """
        raise NotImplementedError

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Return engine health information.
        """
        raise NotImplementedError

    @abstractmethod
    def statistics(self) -> Dict[str, Any]:
        """
        Return engine operational statistics.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def providers(self) -> list[Any]:
        """
        Return the providers registered by this acquisition engine.

        The Runtime uses this during provider discovery to populate
        the canonical Runtime Provider Registry.

        The returned provider objects remain owned by the engine.
        """
        raise NotImplementedError

    @abstractmethod
    def acquire(
        self,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a canonical evidence acquisition cycle.

        Every Evidence Acquisition engine must expose a single
        acquisition entry point regardless of its internal
        synchronization implementation.

        Returns
        -------
        Engine-specific canonical acquisition package.
        """
        raise NotImplementedError