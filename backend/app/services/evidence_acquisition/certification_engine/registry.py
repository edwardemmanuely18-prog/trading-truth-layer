"""
Canonical registry for the Evidence Acquisition Certification Engine.

The registry stores completed certification results.

It does not execute certification or simulation.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .models import (
    CertificationResult,
    CertificationStatistics,
)


class CertificationRegistry:
    """
    Registry of provider certification results.
    """

    def __init__(self) -> None:
        self._results: Dict[str, CertificationResult] = {}

    def register(
        self,
        result: CertificationResult,
    ) -> None:
        """
        Register or replace a provider certification result.
        """
        self._results[result.provider] = result

    def get(
        self,
        provider: str,
    ) -> Optional[CertificationResult]:
        """
        Retrieve a provider certification result.
        """
        return self._results.get(provider)

    def exists(
        self,
        provider: str,
    ) -> bool:
        """
        Check whether a provider has been certified.
        """
        return provider in self._results

    def providers(self) -> List[str]:
        """
        Return all certified providers.
        """
        return sorted(self._results.keys())

    def all(self) -> List[CertificationResult]:
        """
        Return all certification results.
        """
        return list(self._results.values())

    def remove(
        self,
        provider: str,
    ) -> bool:
        """
        Remove a provider certification.
        """
        return self._results.pop(provider, None) is not None

    def clear(self) -> None:
        """
        Remove every certification.
        """
        self._results.clear()

    def statistics(self) -> CertificationStatistics:
        """
        Compute global certification statistics.
        """
        stats = CertificationStatistics()

        stats.providers = len(self._results)

        for result in self._results.values():

            status = result.status.value

            if status == "passed":
                stats.passed += 1

            elif status == "failed":
                stats.failed += 1

            elif status == "warning":
                stats.warnings += 1

            elif status == "pending":
                stats.pending += 1

            elif status == "running":
                stats.running += 1

        return stats


class CertificationRegistryService:
    """
    Public access layer for the certification registry.
    """

    def __init__(self) -> None:
        self._registry = CertificationRegistry()

    def register(
        self,
        result: CertificationResult,
    ) -> None:
        self._registry.register(result)

    def lookup(
        self,
        provider: str,
    ) -> Optional[CertificationResult]:
        return self._registry.get(provider)

    def exists(
        self,
        provider: str,
    ) -> bool:
        return self._registry.exists(provider)

    def providers(self) -> List[str]:
        return self._registry.providers()

    def all(self) -> List[CertificationResult]:
        return self._registry.all()

    def remove(
        self,
        provider: str,
    ) -> bool:
        return self._registry.remove(provider)

    def clear(self) -> None:
        self._registry.clear()

    def statistics(self) -> CertificationStatistics:
        return self._registry.statistics()


__all__ = [
    "CertificationRegistry",
    "CertificationRegistryService",
]