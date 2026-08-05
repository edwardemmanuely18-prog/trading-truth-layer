"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

FIN Parser Tests
"""

from pathlib import Path

from app.services.evidence_acquisition.financial_engine.replay.fixture_loader import (
    FixtureLoader,
)

from app.services.evidence_acquisition.financial_engine.adapters.swift.fin.tokenizer import (
    FINTokenizer,
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


def load_mt103() -> str:

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    fixture = loader.fixtures(
        "MT103",
    )[0]

    return fixture.read_text(
        encoding="utf-8",
    )


# ============================================================================
# Tokenizer
# ============================================================================

def test_tokenizer_discovers_blocks():

    message = load_mt103()

    tokenizer = FINTokenizer()

    tokens = list(
        tokenizer.tokenize(
            message,
        )
    )

    assert len(tokens) == 5

    assert tokens[0].identifier == "1"
    assert tokens[1].identifier == "2"
    assert tokens[2].identifier == "3"
    assert tokens[3].identifier == "4"
    assert tokens[4].identifier == "5"


# ============================================================================
# Block Parser
# ============================================================================

def test_block_parser_builds_fin_message():

    parser = FINBlockParser()

    message = parser.parse(
        load_mt103(),
    )

    assert message.basic_header is not None

    assert message.application_header is not None

    assert message.user_header is not None

    assert message.text is not None

    assert message.trailer is not None


# ============================================================================
# Field Parser
# ============================================================================

def test_field_parser_extracts_business_fields():

    parser = FINBlockParser()

    message = parser.parse(
        load_mt103(),
    )

    fields = FINFieldParser().parse(
        message.text.text,
    )

    assert fields.value("20") == "TTLREF000000001"

    assert fields.value("23B") == "CRED"

    assert fields.value("71A") == "SHA"

    assert fields.value("70") == "TTL REPLAY TEST PAYMENT"


# ============================================================================
# FIN Validation
# ============================================================================

def test_fin_validator_accepts_mt103_fixture():

    parser = FINBlockParser()

    message = parser.parse(
        load_mt103(),
    )

    fields = FINFieldParser().parse(
        message.text.text,
    )

    validator = FINValidator()

    assert validator.validate_currency("USD")

    assert validator.validate_bic(
        "BANKBEBBXXX",
    )

    assert validator.validate_date(
        "260801",
    )

    assert validator.validate_amount(
        "125000.00",
    )

    assert fields.value("32A").startswith(
        "260801USD",
    )