"""
Evidence Acquisition Startup.

Canonical startup orchestration.

No business logic belongs here.

Only orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


# ============================================================
# Startup Step
# ============================================================


@dataclass(slots=True)
class StartupStep:
    """
    Startup execution step.
    """

    name: str

    completed: bool = False

    started_at: datetime | None = None

    completed_at: datetime | None = None

    error: str | None = None


# ============================================================
# Startup Sequence
# ============================================================


class StartupSequence:
    """
    Canonical runtime startup sequence.
    """

    def __init__(self) -> None:

        self.steps: List[StartupStep] = [

            StartupStep("configuration"),

            StartupStep("lifecycle"),

            StartupStep("engines"),

            StartupStep("certification"),

            StartupStep("providers"),

            StartupStep("synchronization"),

            StartupStep("health"),
        ]

    # --------------------------------------------------------

    def step(
        self,
        name: str,
    ) -> StartupStep:

        for step in self.steps:

            if step.name == name:
                return step

        raise KeyError(name)

    # --------------------------------------------------------

    def start(
        self,
        name: str,
    ) -> None:

        step = self.step(name)

        step.started_at = datetime.utcnow()

    # --------------------------------------------------------

    def complete(
        self,
        name: str,
    ) -> None:

        step = self.step(name)

        step.completed = True

        step.completed_at = datetime.utcnow()

    # --------------------------------------------------------

    def fail(
        self,
        name: str,
        error: str,
    ) -> None:

        step = self.step(name)

        step.error = error

    # --------------------------------------------------------

    @property
    def finished(self) -> bool:

        return all(
            step.completed
            for step in self.steps
        )

    # --------------------------------------------------------

    def reset(self) -> None:

        self.__init__()


__all__ = [
    "StartupStep",
    "StartupSequence",
]