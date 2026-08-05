"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Financial Infrastructure Engine

Replay Engine

Coordinates replay execution across Financial Engine datasets.
"""

from __future__ import annotations

from typing import Callable
from typing import Any

from .fixture_loader import FixtureLoader
from .replay_registry import (
    ReplayRegistry,
    replay_registry,
)
from .replay_session import (
    ReplaySession,
    ReplayFixture,
)


# ============================================================================
# Replay Engine
# ============================================================================


class ReplayEngine:
    """
    Canonical Financial Engine replay orchestrator.

    This engine coordinates replay execution while remaining
    completely provider-independent.
    """

    def __init__(
        self,
        loader: FixtureLoader,
        registry: ReplayRegistry | None = None,
    ) -> None:

        self.loader = loader

        self.registry = registry or replay_registry

    # ------------------------------------------------------------------
    # Replay
    # ------------------------------------------------------------------

    def replay(
        self,
        dataset: str,
        processor: Callable[[ReplayFixture], Any],
    ) -> ReplaySession:
        """
        Replay every fixture contained within a dataset.

        The processor callback is responsible for executing the
        Financial Engine acquisition pipeline.
        """

        descriptor = self.registry.dataset(
            dataset,
        )

        if descriptor is None:

            raise ValueError(
                f"Unknown replay dataset '{dataset}'."
            )

        fixtures = self.loader.fixtures(
            dataset,
        )

        session = ReplaySession.create(
            dataset,
        )

        session.begin(
            len(fixtures),
        )

        try:

            for path in fixtures:

                fixture = ReplayFixture(

                    dataset=dataset,

                    path=path,

                    contents=path.read_text(
                        encoding="utf-8",
                    ),
                )

                try:

                    processor(
                        fixture,
                    )

                    session.record_success()

                except Exception:

                    session.record_failure()

            session.complete()

            return session

        except Exception as exc:

            session.fail(
                exc,
            )

            raise

    # ------------------------------------------------------------------
    # Single Fixture Replay
    # ------------------------------------------------------------------

    def replay_fixture(
        self,
        fixture: ReplayFixture,
        processor: Callable[[ReplayFixture], Any],
    ) -> Any:
        """
        Replay a single fixture.
        """

        return processor(
            fixture,
        )

    # ------------------------------------------------------------------
    # Batch Replay
    # ------------------------------------------------------------------

    def replay_all(
        self,
        processor: Callable[[ReplayFixture], Any],
    ) -> list[ReplaySession]:
        """
        Replay every registered dataset.
        """

        sessions = []

        for dataset in self.registry.enabled():

            sessions.append(

                self.replay(

                    dataset.name,

                    processor,
                )

            )

        return sessions

    def supports(
        self,
        dataset: str,
    ) -> bool:

        return (

            self.registry.dataset(
                dataset,
            )

            is not None

        )

    def statistics(
        self,
    ) -> dict:

        enabled = list(
            self.registry.enabled()
        )

        return {

            "datasets": len(enabled),

            "names": [

                dataset.name

                for dataset in enabled

            ],

        }

    def acquire(
        self,
        dataset: str,
        processor: Callable[[ReplayFixture], Any],
    ) -> ReplaySession:
        """
        Canonical acquisition entry point.

        Mirrors live provider acquisition.
        """

        return self.replay(
            dataset,
            processor,
        )

    def health(
        self,
    ) -> dict:

        return {

            "ready": True,

            "datasets": len(

                list(

                    self.registry.enabled()

                )

            ),

        }

    def datasets(
        self,
    ):

        return self.registry.enabled()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "ReplayEngine",
]