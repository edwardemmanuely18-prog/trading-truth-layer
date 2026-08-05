"""
Evidence Acquisition Synchronization.

Canonical synchronization coordinator.

This module coordinates synchronization.

It does not perform synchronization itself.

Synchronization logic belongs inside the individual
acquisition engines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List


# ============================================================
# Synchronization State
# ============================================================


class SynchronizationState(str, Enum):
    """
    Synchronization lifecycle.
    """

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    STOPPED = "stopped"


# ============================================================
# Synchronization Job
# ============================================================


@dataclass(slots=True)
class SynchronizationJob:
    """
    Synchronization job.
    """

    provider: str

    engine: str

    state: SynchronizationState = SynchronizationState.PENDING

    started_at: datetime | None = None

    completed_at: datetime | None = None

    message: str | None = None

    metadata: Dict[str, object] = field(default_factory=dict)


# ============================================================
# Synchronization Coordinator
# ============================================================


class SynchronizationCoordinator:
    """
    Canonical synchronization coordinator.
    """

    def __init__(self) -> None:

        self._jobs: Dict[str, SynchronizationJob] = {}

    # --------------------------------------------------------

    def register(
        self,
        job: SynchronizationJob,
    ) -> None:

        self._jobs[job.provider] = job

    # --------------------------------------------------------

    def unregister(
        self,
        provider: str,
    ) -> None:

        self._jobs.pop(provider, None)

    # --------------------------------------------------------

    def get(
        self,
        provider: str,
    ) -> SynchronizationJob:

        return self._jobs[provider]

    # --------------------------------------------------------

    def exists(
        self,
        provider: str,
    ) -> bool:

        return provider in self._jobs

    # --------------------------------------------------------

    def jobs(self) -> List[SynchronizationJob]:

        return list(self._jobs.values())

    # --------------------------------------------------------

    def start(
        self,
        provider: str,
    ) -> None:

        job = self.get(provider)

        job.state = SynchronizationState.RUNNING

        job.started_at = datetime.utcnow()

    # --------------------------------------------------------

    def complete(
        self,
        provider: str,
        message: str | None = None,
    ) -> None:

        job = self.get(provider)

        job.state = SynchronizationState.COMPLETED

        job.completed_at = datetime.utcnow()

        job.message = message

    # --------------------------------------------------------

    def fail(
        self,
        provider: str,
        message: str,
    ) -> None:

        job = self.get(provider)

        job.state = SynchronizationState.FAILED

        job.completed_at = datetime.utcnow()

        job.message = message

    # --------------------------------------------------------

    def stop(
        self,
        provider: str,
    ) -> None:

        job = self.get(provider)

        job.state = SynchronizationState.STOPPED

        job.completed_at = datetime.utcnow()

    # --------------------------------------------------------

    def running(self) -> List[SynchronizationJob]:

        return [
            job
            for job in self._jobs.values()
            if job.state == SynchronizationState.RUNNING
        ]

    # --------------------------------------------------------

    def completed(self) -> List[SynchronizationJob]:

        return [
            job
            for job in self._jobs.values()
            if job.state == SynchronizationState.COMPLETED
        ]

    # --------------------------------------------------------

    def failed(self) -> List[SynchronizationJob]:

        return [
            job
            for job in self._jobs.values()
            if job.state == SynchronizationState.FAILED
        ]

    # --------------------------------------------------------

    def clear(self) -> None:

        self._jobs.clear()


__all__ = [
    "SynchronizationState",
    "SynchronizationJob",
    "SynchronizationCoordinator",
]