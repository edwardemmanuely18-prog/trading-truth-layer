"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Adapter Integration Tests

Offline integration tests driven entirely by replay fixtures.

No live SWIFT connectivity is required.
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

from app.services.evidence_acquisition.financial_engine.adapters.swift.fin.validator import (
    FINValidator,
)


FIXTURE_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
    / "tests"
    / "financial"
    / "swift"
)


def load_fixture(dataset: str):

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    return loader.fixtures(
        dataset,
    )[0].read_text(
        encoding="utf-8",
    )


# ============================================================================
# MT103 End-to-End Parsing
# ============================================================================

def test_mt103_offline_pipeline():

    raw = load_fixture(
        "MT103",
    )

    parser = FINBlockParser()

    message = parser.parse(
        raw,
    )

    fields = FINFieldParser().parse(
        message.text.text,
    )

    validator = FINValidator()

    assert validator.validate_currency(
        "USD",
    )

    assert validator.validate_date(
        "260801",
    )

    assert validator.validate_bic(
        fields.require("52A"),
    )

    assert fields.require("20") == "TTLREF000000001"

    assert fields.require("23B") == "CRED"

    assert fields.require("71A") == "SHA"

    assert message.application_header.message_type == "103"