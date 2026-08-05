"""
Evidence Acquisition Health.

Canonical runtime health monitoring.

This module owns runtime health state only.

It does not perform synchronization or certification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List


# ============================================================
# Health Status
# ============================================================


class HealthStatus(str, Enum):
    """
    Runtime health status.
    """

    UNKNOWN = "unknown"

    HEALTHY = "healthy"

    DEGRADED = "degraded"

    UNHEALTHY = "unhealthy"


# ============================================================
# Health Check
# ============================================================


@dataclass(slots=True)
class HealthCheck:
    """
    Health information for a runtime component.
    """

    component: str

    status: HealthStatus = HealthStatus.UNKNOWN

    checked_at: datetime | None = None

    message: str | None = None

    metadata: Dict[str, object] = field(default_factory=dict)


# ============================================================
# Health Monitor
# ============================================================


class HealthMonitor:
    """
    Canonical runtime health monitor.
    """

    def __init__(self) -> None:

        self._checks: Dict[str, HealthCheck] = {}

    # --------------------------------------------------------

    def register(
        self,
        component: str,
    ) -> None:

        self._checks[component] = HealthCheck(
            component=component
        )

    # --------------------------------------------------------

    def unregister(
        self,
        component: str,
    ) -> None:

        self._checks.pop(component, None)

    # --------------------------------------------------------

    def update(
        self,
        component: str,
        status: HealthStatus,
        message: str | None = None,
        metadata: Dict[str, object] | None = None,
    ) -> None:

        if component not in self._checks:

            self.register(component)

        check = self._checks[component]

        check.status = status

        check.checked_at = datetime.utcnow()

        check.message = message

        if metadata is not None:

            check.metadata = metadata

    # --------------------------------------------------------

    def get(
        self,
        component: str,
    ) -> HealthCheck:

        return self._checks[component]

    # --------------------------------------------------------

    def checks(self) -> List[HealthCheck]:

        return list(self._checks.values())

    # --------------------------------------------------------

    def healthy(self) -> List[HealthCheck]:

        return [
            check
            for check in self._checks.values()
            if check.status == HealthStatus.HEALTHY
        ]

    # --------------------------------------------------------

    def unhealthy(self) -> List[HealthCheck]:

        return [
            check
            for check in self._checks.values()
            if check.status == HealthStatus.UNHEALTHY
        ]

    # --------------------------------------------------------

    def degraded(self) -> List[HealthCheck]:

        return [
            check
            for check in self._checks.values()
            if check.status == HealthStatus.DEGRADED
        ]

    # --------------------------------------------------------

    def overall(self) -> HealthStatus:
        """
        Overall runtime health.
        """

        statuses = {
            check.status
            for check in self._checks.values()
        }

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY

        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED

        if statuses:
            return HealthStatus.HEALTHY

        return HealthStatus.UNKNOWN

    # --------------------------------------------------------

    def clear(self) -> None:

        self._checks.clear()


__all__ = [
    "HealthStatus",
    "HealthCheck",
    "HealthMonitor",
]