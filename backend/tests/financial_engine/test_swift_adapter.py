"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Adapter Tests

Validates that the SWIFT adapter can consume replay fixtures
without requiring a live SWIFT connection.
"""

from pathlib import Path

from app.services.evidence_acquisition.financial_engine.replay.fixture_loader import (
    FixtureLoader,
)

from app.services.evidence_acquisition.financial_engine.adapters.swift.fin.block_parser import (
    FINBlockParser,
)

from app.services.evidence_acquisition.financial_engine.adapters.swift.fin.field_parser import (
    FINFieldParser,
)

from app.services.evidence_acquisition.financial_engine.adapters.swift.fin.registry import (
    FIN_REGISTRY,
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


def load_mt103():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    return loader.fixtures(
        "MT103",
    )[0].read_text(
        encoding="utf-8",
    )


# ============================================================================
# Adapter Parsing
# ============================================================================

def test_mt103_message_type():

    parser = FINBlockParser()

    message = parser.parse(
        load_mt103(),
    )

    assert (
        message.application_header.message_type
        == "103"
    )


def test_mt103_registered():

    specification = FIN_REGISTRY.specification(
        "MT103",
    )

    assert specification is not None

    assert (
        specification.message_type
        == "MT103"
    )


def test_mt103_fields():

    parser = FINBlockParser()

    message = parser.parse(
        load_mt103(),
    )

    fields = FINFieldParser().parse(
        message.text.text,
    )

    assert fields.require("20") == "TTLREF000000001"

    assert fields.require("23B") == "CRED"

    assert fields.require("71A") == "SHA"

    assert fields.require("70") == "TTL REPLAY TEST PAYMENT"


def test_mt103_amount():

    parser = FINBlockParser()

    message = parser.parse(
        load_mt103(),
    )

    fields = FINFieldParser().parse(
        message.text.text,
    )

    amount = fields.require(
        "32A",
    )

    assert amount.startswith(
        "260801USD",
    )