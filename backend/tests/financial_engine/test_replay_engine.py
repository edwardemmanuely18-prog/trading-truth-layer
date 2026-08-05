"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Replay Engine Tests
"""

from pathlib import Path

from app.services.evidence_acquisition.financial_engine.replay.fixture_loader import (
    FixtureLoader,
)

from app.services.evidence_acquisition.financial_engine.replay.replay_engine import (
    ReplayEngine,
)

from app.services.evidence_acquisition.financial_engine.replay.replay_registry import (
    replay_registry,
)


# ============================================================================
# Fixtures
# ============================================================================

FIXTURE_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
    / "tests"
    / "financial"
    / "swift"
)


# ============================================================================
# Replay
# ============================================================================

def test_replay_mt103_dataset():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    engine = ReplayEngine(
        loader=loader,
        registry=replay_registry,
    )

    processed = []

    session = engine.replay(

        "MT103",

        lambda fixture: processed.append(
            fixture.path.name,
        ),
    )

    assert session.successful

    assert session.total == 1

    assert session.successful_replays == 1

    assert session.failed_replays == 0

    assert len(processed) == 1

    assert processed[0] == "MT103_001.txt"


# ============================================================================
# Replay All
# ============================================================================

def test_replay_all_registered_datasets():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    engine = ReplayEngine(
        loader=loader,
        registry=replay_registry,
    )

    sessions = engine.replay_all(

        lambda fixture: None,
    )

    assert len(sessions) > 0

    assert all(
        session.successful
        for session in sessions
    )


# ============================================================================
# Statistics
# ============================================================================

def test_replay_statistics():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    engine = ReplayEngine(
        loader=loader,
        registry=replay_registry,
    )

    session = engine.replay(

        "MT103",

        lambda fixture: fixture,
    )

    assert session.started_at is not None

    assert session.completed_at is not None

    assert session.duration_seconds >= 0

    assert session.total == 1

    assert session.successful_replays == 1

    assert session.failed_replays == 0


# ============================================================================
# Failure Recording
# ============================================================================

def test_replay_records_failures():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    engine = ReplayEngine(
        loader=loader,
        registry=replay_registry,
    )

    def failing_processor(_):

        raise RuntimeError(
            "Replay failure",
        )

    session = engine.replay(

        "MT103",

        failing_processor,
    )

    assert not session.successful

    assert session.total == 1

    assert session.successful_replays == 0

    assert session.failed_replays == 1


# ============================================================================
# MT202 Replay
# ============================================================================

def test_replay_mt202_dataset():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    engine = ReplayEngine(
        loader=loader,
        registry=replay_registry,
    )

    processed = []

    fixtures = loader.fixtures(
        "MT202",
    )

    expected = len(
        fixtures,
    )

    session = engine.replay(

        "MT202",

        lambda fixture: processed.append(
            fixture.path.name,
        ),
    )

    assert session.successful

    assert session.total == expected

    assert session.successful_replays == expected

    assert session.failed_replays == 0

    assert len(processed) == expected


# ============================================================================
# MT202 Dataset Discovery
# ============================================================================

def test_mt202_dataset_registered():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    datasets = loader.datasets()

    assert "MT202" in datasets


# ============================================================================
# MT202 Fixture Discovery
# ============================================================================

def test_mt202_fixture_discovery():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    fixtures = loader.fixtures(
        "MT202",
    )

    assert len(fixtures) > 0


# ============================================================================
# Replay Statistics (MT202)
# ============================================================================

def test_mt202_replay_statistics():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    engine = ReplayEngine(
        loader=loader,
        registry=replay_registry,
    )

    fixtures = loader.fixtures(
        "MT202",
    )

    expected = len(
        fixtures,
    )

    session = engine.replay(

        "MT202",

        lambda fixture: fixture,
    )

    assert session.started_at is not None

    assert session.completed_at is not None

    assert session.duration_seconds >= 0

    assert session.total == expected

    assert session.successful_replays == expected

    assert session.failed_replays == 0


# ============================================================================
# MT700 Replay
# ============================================================================

def test_replay_mt700_dataset():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    engine = ReplayEngine(
        loader=loader,
        registry=replay_registry,
    )

    processed = []

    fixtures = loader.fixtures(
        "MT700",
    )

    expected = len(
        fixtures,
    )

    session = engine.replay(

        "MT700",

        lambda fixture: processed.append(
            fixture.path.name,
        ),
    )

    assert session.successful

    assert session.total == expected

    assert session.successful_replays == expected

    assert session.failed_replays == 0

    assert len(processed) == expected


# ============================================================================
# MT700 Dataset Discovery
# ============================================================================

def test_mt700_dataset_registered():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    datasets = loader.datasets()

    assert "MT700" in datasets


# ============================================================================
# MT700 Fixture Discovery
# ============================================================================

def test_mt700_fixture_discovery():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    fixtures = loader.fixtures(
        "MT700",
    )

    assert len(fixtures) > 0


# ============================================================================
# Replay Statistics (MT700)
# ============================================================================

def test_mt700_replay_statistics():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    engine = ReplayEngine(
        loader=loader,
        registry=replay_registry,
    )

    fixtures = loader.fixtures(
        "MT700",
    )

    expected = len(
        fixtures,
    )

    session = engine.replay(

        "MT700",

        lambda fixture: fixture,
    )

    assert session.started_at is not None

    assert session.completed_at is not None

    assert session.duration_seconds >= 0

    assert session.total == expected

    assert session.successful_replays == expected

    assert session.failed_replays == 0