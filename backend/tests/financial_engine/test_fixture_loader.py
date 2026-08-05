"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Fixture Loader Tests
"""

from pathlib import Path

from app.services.evidence_acquisition.financial_engine.replay.fixture_loader import (
    FixtureLoader,
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
# Tests
# ============================================================================


def test_fixture_directory_exists():

    assert FIXTURE_ROOT.exists()


def test_mt103_dataset_exists():

    dataset = (
        FIXTURE_ROOT
        / "MT103"
    )

    assert dataset.exists()


def test_fixture_loader_discovers_mt103():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    fixtures = loader.fixtures(
        "MT103",
    )

    assert len(fixtures) > 0


def test_first_fixture_is_txt():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    fixtures = loader.fixtures(
        "MT103",
    )

    assert fixtures[0].suffix == ".txt"


def test_fixture_contains_swift_message():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    fixture = loader.fixtures(
        "MT103",
    )[0]

    text = fixture.read_text(
        encoding="utf-8",
    )

    assert "{1:" in text

    assert "{2:" in text

    assert "{4:" in text