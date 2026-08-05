"""
Evidence Acquisition Lifecycle.

Defines the canonical lifecycle state machine used by the
Evidence Acquisition Runtime.

This module owns lifecycle policy only.

It intentionally contains no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


# ============================================================
# Lifecycle State
# ============================================================


class LifecycleState(str, Enum):
    """
    Canonical lifecycle state.
    """

    CREATED = "created"

    INITIALIZING = "initializing"

    READY = "ready"

    STARTING = "starting"

    RUNNING = "running"

    STOPPING = "stopping"

    STOPPED = "stopped"

    FAILED = "failed"


# ============================================================
# Lifecycle Event
# ============================================================


@dataclass(slots=True)
class LifecycleEvent:
    """
    Lifecycle transition event.
    """

    previous_state: LifecycleState

    current_state: LifecycleState

    timestamp: datetime = field(default_factory=datetime.utcnow)

    reason: Optional[str] = None


# ============================================================
# Lifecycle
# ============================================================


class Lifecycle:
    """
    Canonical runtime lifecycle controller.

    Owns lifecycle state transitions and records
    every transition for auditing.
    """

    def __init__(self) -> None:

        self._state = LifecycleState.CREATED

        self._history: list[LifecycleEvent] = []

    # --------------------------------------------------------

    @property
    def state(self) -> LifecycleState:

        return self._state

    # --------------------------------------------------------

    @property
    def history(self) -> list[LifecycleEvent]:

        return list(self._history)

    # --------------------------------------------------------

    def transition(
        self,
        state: LifecycleState,
        reason: Optional[str] = None,
    ) -> None:
        """
        Transition lifecycle to a new state.
        """

        event = LifecycleEvent(
            previous_state=self._state,
            current_state=state,
            reason=reason,
        )

        self._history.append(event)

        self._state = state

    # ========================================================
    # Canonical State Transitions
    # ========================================================

    def created(self) -> None:
        """
        Transition to CREATED.
        """

        self.transition(
            LifecycleState.CREATED,
        )

    # --------------------------------------------------------

    def initializing(self) -> None:
        """
        Transition to INITIALIZING.
        """

        self.transition(
            LifecycleState.INITIALIZING,
        )

    # --------------------------------------------------------

    def ready(self) -> None:
        """
        Transition to READY.
        """

        self.transition(
            LifecycleState.READY,
        )

    # --------------------------------------------------------

    def starting(self) -> None:
        """
        Transition to STARTING.
        """

        self.transition(
            LifecycleState.STARTING,
        )

    # --------------------------------------------------------

    def running(self) -> None:
        """
        Transition to RUNNING.
        """

        self.transition(
            LifecycleState.RUNNING,
        )

    # --------------------------------------------------------

    def stopping(self) -> None:
        """
        Transition to STOPPING.
        """

        self.transition(
            LifecycleState.STOPPING,
        )

    # --------------------------------------------------------

    def stopped(self) -> None:
        """
        Transition to STOPPED.
        """

        self.transition(
            LifecycleState.STOPPED,
        )

    # --------------------------------------------------------

    def failed(
        self,
        reason: Optional[str] = None,
    ) -> None:
        """
        Transition to FAILED.
        """

        self.transition(
            LifecycleState.FAILED,
            reason,
        )

    # ========================================================
    # Utilities
    # ========================================================

    def reset(self) -> None:
        """
        Reset lifecycle history.
        """

        self._history.clear()

        self._state = LifecycleState.CREATED

    # --------------------------------------------------------

    def statistics(self) -> Dict[str, object]:
        """
        Lifecycle metrics.
        """

        return {
            "transitions": len(self._history),
            "current_state": self._state.value,
            "created_at": (
                self._history[0].timestamp
                if self._history
                else None
            ),
            "last_transition": (
                self._history[-1].timestamp
                if self._history
                else None
            ),
        }


__all__ = [
    "LifecycleState",
    "LifecycleEvent",
    "Lifecycle",
]