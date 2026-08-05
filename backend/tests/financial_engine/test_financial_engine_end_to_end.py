"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

End-to-End Tests

Institutional verification of the complete Financial
Infrastructure Engine pipeline.

Pipeline

Replay
    ↓
FIN Parser
    ↓
SWIFT Adapter
    ↓
Normalizer
    ↓
Translation
    ↓
Validation
    ↓
Registry
    ↓
Synchronizer
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.evidence_acquisition.financial_engine.adapters.swift.swift_adapter import (
    SwiftAdapter,
    SwiftConfiguration,
)

from app.services.evidence_acquisition.financial_engine.adapters.swift.fin.block_parser import (
    FINBlockParser,
)

from app.services.evidence_acquisition.financial_engine.normalizer import (
    FinancialEvidenceNormalizer,
)

from app.services.evidence_acquisition.financial_engine.provider import (
    FinancialProvider,
    ProviderCapability,
    ProviderDescriptor,
)

from app.services.evidence_acquisition.financial_engine.registry import (
    FinancialRegistryService,
)

from app.services.evidence_acquisition.financial_engine.replay.bootstrap import (
    register_replay_datasets,
)

from app.services.evidence_acquisition.financial_engine.replay.fixture_loader import (
    FixtureLoader,
)

from app.services.evidence_acquisition.financial_engine.replay.replay_engine import (
    ReplayEngine,
)

from app.services.evidence_acquisition.financial_engine.replay.replay_registry import (
    replay_registry,
)

from app.services.evidence_acquisition.financial_engine.synchronizer import (
    FinancialSynchronizer,
)

from app.services.evidence_acquisition.financial_engine.translators import (
    TranslationRegistry,
    TranslationService,
)

from app.services.evidence_acquisition.financial_engine.validators import (
    ValidationService,
    ValidatorRegistry,
)

from app.services.evidence_acquisition.financial_engine.connectors import (
    FinancialConnector,
)



# ============================================================================
# Fixtures
# ============================================================================

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

FIXTURE_ROOT = (
    REPOSITORY_ROOT
    / "tests"
    / "financial"
    / "swift"
)

@pytest.fixture
def replay_engine():

    replay_registry.clear()

    register_replay_datasets(
        FIXTURE_ROOT,
    )

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    return ReplayEngine(
        loader=loader,
        registry=replay_registry,
    )

@pytest.fixture
def registry():

    return FinancialRegistryService()

@pytest.fixture
def translation_service():

    return TranslationService(
        TranslationRegistry(),
    )

@pytest.fixture
def validation_service():

    return ValidationService(
        ValidatorRegistry(),
    )

@pytest.fixture
def normalizer():

    return FinancialEvidenceNormalizer()

@pytest.fixture
def synchronizer(

    registry,

    translation_service,

    validation_service,

):

    return FinancialSynchronizer(

        registry,

        translation_service,

        validation_service,
    )

class OfflineConnector(FinancialConnector):

    def __init__(self):

        super().__init__(
            configuration={},
        )

    @property
    def connected(self):

        return True

    @property
    def authenticated(self):

        return True

    def provider_name(self):

        return "SWIFT"

    def connect(self):

        return True

    def disconnect(self):

        return True

    def authenticate(self):

        return True

    def health_check(self):

        return True

    def ping(self):

        return True


def build_adapter(
    replay_dataset: str = "MT103",
    timeout: int = 30,
):

    connector = OfflineConnector()

    replay_registry.clear()

    register_replay_datasets(
        FIXTURE_ROOT,
    )

    configuration = SwiftConfiguration(

        token_url="https://offline.test/token",

        client_id="offline",

        client_secret="offline",

        api_base_url="https://offline.test/api",

        timeout=timeout,

        replay_enabled=True,

        replay_dataset=replay_dataset,

        fixtures_directory=str(
            FIXTURE_ROOT,
        ),
    )

    return SwiftAdapter(

        connector=connector,

        configuration=configuration,
    )

def replay_fixture_count(
    dataset: str,
) -> int:

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    return len(

        loader.fixtures(
            dataset,
        )

    )

def assert_successful_session(
    session,
    expected: int,
    dataset: str,
):

    assert session.successful

    assert session.dataset == dataset

    assert session.fixture_count == expected

    assert session.processed_count == expected

    assert session.failed_count == 0

def assert_fin_message(
    message,
    message_type: str,
):

    assert message is not None

    assert message.basic_header is not None

    assert message.application_header is not None

    assert message.text is not None

    assert (
        message.application_header.message_type
        == message_type
    )

def assert_parsed_messages(
    parsed,
    message_type: str,
):

    valid_messages = [

        message

        for message in parsed

        if (
            message.application_header is not None
            and message.application_header.message_type
            is not None
        )

    ]

    assert len(
        valid_messages
    ) > 0

    assert all(

        message.application_header.message_type
        == message_type

        for message in valid_messages

    )

def load_fixture(
    dataset: str,
    fixture_index: int = 0,
):

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    fixtures = loader.fixtures(
        dataset,
    )

    if not fixtures:

        raise FileNotFoundError(
            f"No fixtures found for dataset '{dataset}'."
        )

    return fixtures[
        fixture_index
    ].read_text(
        encoding="utf-8",
    )

def load_mt202():

    loader = FixtureLoader(
        FIXTURE_ROOT,
    )

    fixture = loader.fixtures(
        "MT202",
    )[0]

    return fixture.read_text(
        encoding="utf-8",
    )

def build_fin_message(
    dataset: str = "MT103",
    fixture_index: int = 0,
):

    parser = FINBlockParser()

    return parser.parse(

        load_fixture(

            dataset,

            fixture_index,

        )

    )

# ============================================================================
# Replay Pipeline
# ============================================================================


def test_mt103_replay_pipeline(
    replay_engine,
):
    """
    Verify the Replay Engine discovers and replays the MT103 dataset.
    """

    processed = []

    session = replay_engine.replay(

        "MT103",

        lambda fixture: processed.append(
            fixture.path.name,
        ),
    )

    assert session is not None

    assert session.successful

    assert session.total == 1

    assert session.processed_count == 1

    assert session.failed_count == 0

    assert len(processed) == 1

    assert processed[0].endswith(".txt")


# ============================================================================
# FIN Parser Pipeline
# ============================================================================


def test_fin_parser_pipeline():
    """
    Verify the FIN parser successfully parses the replay fixture.
    """

    message = build_fin_message()

    assert_fin_message(

        message,

        "103",

    )

    assert message.user_header is not None

    assert message.trailer is not None

    assert message.text.text is not None

    assert (
        ":20:TTLREF000000001"
        in message.text.text
    )

    assert (
        ":23B:CRED"
        in message.text.text
    )

    assert (
        ":71A:SHA"
        in message.text.text
    )


# ============================================================================
# Replay -> Parser Integration
# ============================================================================


def test_replay_parser_integration(
    replay_engine,
):
    """
    Verify every replay fixture can be parsed into a FINMessage.
    """

    parser = FINBlockParser()

    parsed = []

    def process(
        fixture,
    ):

        message = parser.parse(
            fixture.contents,
        )

        parsed.append(
            message,
        )

    session = replay_engine.replay(

        "MT103",

        process,
    )

    assert session.successful

    assert session.failed_count == 0

    assert len(parsed) == 1

    assert_parsed_messages(

        parsed,

        "103",

    )

    assert parsed[0].text.text is not None


# ============================================================================
# SWIFT Replay Acquisition
# ============================================================================


def test_swift_adapter_replay_pipeline():
    """
    Verify the adapter executes the complete replay acquisition pipeline.
    """

    adapter = build_adapter()

    session = adapter.acquire_replay()

    assert session is not None

    assert session.successful

    assert session.fixture_count == 1

    assert session.processed_count == 1

    assert session.failed_count == 0

    assert session.dataset == "MT103"


# ============================================================================
# SWIFT Normalized Acquisition
# ============================================================================


def test_swift_adapter_acquire_pipeline():
    """
    Verify the adapter returns the canonical normalized
    Financial Engine acquisition payload.
    """

    adapter = build_adapter()

    payload = adapter.acquire()

    assert payload is not None

    assert isinstance(
        payload,
        dict,
    )

    assert payload["connector_name"] == "SWIFT"

    assert payload["connector_version"] is not None

    assert payload["schema_version"] == "1.0"

    assert "replay_session" in payload

    session = payload["replay_session"]

    assert session.successful

    assert session.processed_count == 1


# ============================================================================
# Provider Descriptor
# ============================================================================


def test_swift_adapter_descriptor():
    """
    Verify provider descriptor metadata.
    """

    adapter = build_adapter()

    descriptor = adapter.descriptor()

    assert descriptor.name == "SWIFT"

    assert descriptor.display_name

    assert descriptor.vendor

    assert descriptor.version

    assert descriptor.description


# ============================================================================
# Provider Capability
# ============================================================================


def test_swift_adapter_capability():
    """
    Verify provider capability declaration.
    """

    adapter = build_adapter()

    capability = adapter.capability()

    assert capability.streaming is False

    assert capability.historical_sync

    assert capability.incremental_sync

    assert capability.batch_sync

    assert capability.authentication == "OAuth2"


# ============================================================================
# Provider Connectivity
# ============================================================================


def test_swift_adapter_connectivity():
    """
    Verify provider connectivity state.
    """

    adapter = build_adapter()

    assert adapter.connected()

    assert adapter.authenticated()

    assert adapter.healthy


# ============================================================================
# Replay Payload Integrity
# ============================================================================


def test_swift_adapter_replay_payload():
    """
    Verify replay mode returns the replay session through the
    canonical acquisition contract.
    """

    adapter = build_adapter()

    payload = adapter.acquire()

    session = payload["replay_session"]

    assert session.dataset == "MT103"

    assert session.fixture_count == 1

    assert session.processed_count == 1

    assert session.failed_count == 0


# ============================================================================
# MT202 Replay Pipeline
# ============================================================================

def test_mt202_replay_pipeline(
    replay_engine,
):
    """
    Verify the Replay Engine discovers and replays the MT202 dataset.
    """

    processed = []

    expected = replay_fixture_count(
        "MT202",
    )

    session = replay_engine.replay(

        "MT202",

        lambda fixture: processed.append(
            fixture.path.name,
        ),
    )

    assert session is not None

    assert session.successful

    assert session.total == expected

    assert session.processed_count == expected

    assert session.failed_count == 0

    assert len(processed) == expected


# ============================================================================
# MT202 FIN Parser Pipeline
# ============================================================================

def test_mt202_fin_parser_pipeline():
    """
    Verify the FIN parser successfully parses the MT202 replay fixture.
    """

    message = build_fin_message(
        "MT202",
    )

    assert_fin_message(

        message,

        "202",

    )


# ============================================================================
# MT202 Replay -> Parser Integration
# ============================================================================

def test_mt202_replay_parser_integration(
    replay_engine,
):
    """
    Verify every MT202 replay fixture can be parsed into a FINMessage.
    """

    parser = FINBlockParser()

    parsed = []

    fixtures = FixtureLoader(
        FIXTURE_ROOT,
    ).fixtures(
        "MT202",
    )

    expected = len(
        fixtures,
    )

    def process(
        fixture,
    ):

        parsed.append(

            parser.parse(
                fixture.contents,
            )

        )

    session = replay_engine.replay(

        "MT202",

        process,
    )

    assert session.successful

    assert session.failed_count == 0

    assert len(parsed) == expected

    assert_parsed_messages(

        parsed,

        "202",

    )


# ============================================================================
# MT700 Replay Pipeline
# ============================================================================

def test_mt700_replay_pipeline(
    replay_engine,
):
    """
    Verify the Replay Engine discovers and replays the MT700 dataset.
    """

    processed = []

    expected = replay_fixture_count(
        "MT700",
    )

    session = replay_engine.replay(

        "MT700",

        lambda fixture: processed.append(
            fixture.path.name,
        ),
    )

    assert session is not None

    assert_successful_session(

        session,

        expected,

        "MT700",

    )

    assert len(processed) == expected


# ============================================================================
# MT700 FIN Parser Pipeline
# ============================================================================

def test_mt700_fin_parser_pipeline():
    """
    Verify the FIN parser successfully parses the MT700 replay fixture.
    """

    message = build_fin_message(
        "MT700",
    )

    assert_fin_message(

        message,

        "700",

    )


# ============================================================================
# MT700 Replay -> Parser Integration
# ============================================================================

def test_mt700_replay_parser_integration(
    replay_engine,
):
    """
    Verify every MT700 replay fixture can be parsed into a FINMessage.
    """

    parser = FINBlockParser()

    parsed = []

    fixtures = FixtureLoader(
        FIXTURE_ROOT,
    ).fixtures(
        "MT700",
    )

    expected = len(
        fixtures,
    )

    def process(
        fixture,
    ):

        parsed.append(

            parser.parse(
                fixture.contents,
            )

        )

    session = replay_engine.replay(

        "MT700",

        process,
    )

    assert session.successful

    assert session.failed_count == 0

    assert len(parsed) == expected

    assert_parsed_messages(

        parsed,

        "700",

    )