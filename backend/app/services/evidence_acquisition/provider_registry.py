"""
Evidence Acquisition Provider Registry.

Operational registry of providers available to the Evidence
Acquisition Runtime.

NOTE
----
This registry does NOT perform certification.

Certification is owned by:

    certification_engine.registry

This registry only manages providers that are available
for runtime operation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


# ============================================================
# Provider State
# ============================================================


class ProviderState(str, Enum):
    """
    Runtime provider state.
    """

    REGISTERED = "registered"

    CERTIFIED = "certified"

    ACTIVE = "active"

    SYNCHRONIZING = "synchronizing"

    STOPPED = "stopped"

    FAILED = "failed"


# ============================================================
# Provider Record
# ============================================================


@dataclass(slots=True)
class ProviderRecord:
    """
    Runtime provider record.
    """

    name: str

    engine: str

    provider: Any

    state: ProviderState = ProviderState.REGISTERED

    certified: bool = False

    active: bool = False

    connected: bool = False

    registered_at: datetime = field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# Statistics
# ============================================================


@dataclass(slots=True)
class ProviderStatistics:
    """
    Provider registry statistics.
    """

    total: int = 0

    certified: int = 0

    active: int = 0

    synchronizing: int = 0

    failed: int = 0


# ============================================================
# Registry
# ============================================================


class ProviderRegistry:
    """
    Runtime provider registry.
    """

    def __init__(self) -> None:

        self._providers: Dict[str, ProviderRecord] = {}

    # --------------------------------------------------------

    def register(self, record: ProviderRecord) -> None:

        self._providers[record.name] = record

    # --------------------------------------------------------

    def unregister(self, name: str) -> None:

        self._providers.pop(name, None)

    # --------------------------------------------------------

    def exists(self, name: str) -> bool:

        return name in self._providers

    # --------------------------------------------------------

    def get(self, name: str) -> ProviderRecord:

        if name not in self._providers:
            raise KeyError(f"Unknown provider '{name}'.")

        return self._providers[name]

    # --------------------------------------------------------

    def providers(self) -> List[ProviderRecord]:

        return list(self._providers.values())

    # --------------------------------------------------------

    def active(self) -> List[ProviderRecord]:

        return [
            provider
            for provider in self._providers.values()
            if provider.active
        ]

    # --------------------------------------------------------

    def inactive(self) -> List[ProviderRecord]:

        return [
            provider
            for provider in self._providers.values()
            if not provider.active
        ]

    # --------------------------------------------------------

    def certified(self) -> List[ProviderRecord]:

        return [
            provider
            for provider in self._providers.values()
            if provider.certified
        ]

    # --------------------------------------------------------

    def clear(self) -> None:

        self._providers.clear()

    # --------------------------------------------------------

    def statistics(self) -> ProviderStatistics:

        providers = list(self._providers.values())

        return ProviderStatistics(
            total=len(providers),
            certified=sum(
                provider.certified
                for provider in providers
            ),
            active=sum(
                provider.active
                for provider in providers
            ),
            synchronizing=sum(
                provider.state == ProviderState.SYNCHRONIZING
                for provider in providers
            ),
            failed=sum(
                provider.state == ProviderState.FAILED
                for provider in providers
            ),
        )


__all__ = [
    "ProviderState",
    "ProviderRecord",
    "ProviderStatistics",
    "ProviderRegistry",
]