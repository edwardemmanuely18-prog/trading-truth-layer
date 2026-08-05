"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Financial Infrastructure Engine

Replay Session

Represents a single replay execution lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from pathlib import Path
from typing import Optional


# ============================================================================
# Replay Session
# ============================================================================


@dataclass(slots=True)
class ReplaySession:
    """
    Represents a single replay execution.

    A replay session tracks one execution of a replay dataset
    through the Financial Engine.
    """

    session_id: str

    dataset: str

    started_at: datetime

    completed_at: Optional[datetime] = None

    successful: bool = False

    fixture_count: int = 0

    processed_count: int = 0

    failed_count: int = 0

    error: Exception | None = None

    @classmethod
    def create(
        cls,
        dataset: str,
    ) -> "ReplaySession":
        """
        Create a new replay session.
        """

        return cls(
            session_id=str(uuid4()),
            dataset=dataset,
            started_at=datetime.utcnow(),
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def begin(
        self,
        fixture_count: int,
    ) -> None:
        """
        Initialize replay statistics.
        """

        self.fixture_count = fixture_count

    def record_success(
        self,
    ) -> None:
        """
        Record one successful replay.
        """

        self.processed_count += 1

    def record_failure(
        self,
    ) -> None:
        """
        Record one failed replay.
        """

        self.failed_count += 1

    def complete(
        self,
    ) -> None:
        """
        Mark replay as complete.
        """

        self.completed_at = datetime.utcnow()

        self.successful = (
            self.failed_count == 0
        )

    def fail(
        self,
        error: Exception,
    ) -> None:
        """
        Mark replay execution as failed.
        """

        self.error = error

        self.completed_at = datetime.utcnow()

        self.successful = False

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def completion_ratio(
        self,
    ) -> float:

        if self.fixture_count == 0:

            return 0.0

        return (
            self.processed_count
            / self.fixture_count
        )

    @property
    def remaining(
        self,
    ) -> int:

        return max(
            self.fixture_count
            - self.processed_count
            - self.failed_count,
            0,
        )

    @property
    def total(
        self,
    ) -> int:
        """
        Total number of replay fixtures.
        """

        return self.fixture_count

    @property
    def successful_replays(
        self,
    ) -> int:
        """
        Number of successfully processed fixtures.
        """

        return self.processed_count

    @property
    def failed_replays(
        self,
    ) -> int:
        """
        Number of failed fixtures.
        """

        return self.failed_count

    @property
    def duration_seconds(
        self,
    ) -> float:
        """
        Replay execution duration in seconds.
        """

        if self.completed_at is None:

            return 0.0

        return (

            self.completed_at
            - self.started_at

        ).total_seconds()


# ============================================================================
# Replay Dataset
# ============================================================================


@dataclass(slots=True)
class ReplayFixture:
    """
    Represents one replay fixture.
    """

    dataset: str

    path: Path

    contents: str


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "ReplaySession",
    "ReplayFixture",
]