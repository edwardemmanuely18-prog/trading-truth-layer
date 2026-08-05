"""
Evidence Acquisition Shutdown.

Canonical shutdown orchestration.

Owns the shutdown sequence only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


# ============================================================
# Shutdown Step
# ============================================================


@dataclass(slots=True)
class ShutdownStep:
    """
    Shutdown execution step.
    """

    name: str

    completed: bool = False

    started_at: datetime | None = None

    completed_at: datetime | None = None

    error: str | None = None


# ============================================================
# Shutdown Sequence
# ============================================================


class ShutdownSequence:
    """
    Canonical runtime shutdown sequence.
    """

    def __init__(self) -> None:

        self.steps: List[ShutdownStep] = [

            ShutdownStep("health"),

            ShutdownStep("synchronization"),

            ShutdownStep("providers"),

            ShutdownStep("engines"),

            ShutdownStep("certification"),

            ShutdownStep("lifecycle"),
        ]

    # --------------------------------------------------------

    def step(
        self,
        name: str,
    ) -> ShutdownStep:

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
    "ShutdownStep",
    "ShutdownSequence",
]