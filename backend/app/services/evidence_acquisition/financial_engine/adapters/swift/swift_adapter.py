"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Adapter

Institutional Financial Adapter implementation for SWIFT.

This adapter composes all SWIFT services into a single
provider for the Financial Engine.

Responsibilities
----------------
• Provider metadata
• Provider capabilities
• Client orchestration
• Native evidence acquisition

Translation and validation remain the responsibility of the
Financial Engine.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import List
from typing import Any

from ..base_adapter import FinancialAdapter

from ...provider import (
    ProviderCapability,
    ProviderDescriptor,
)

from ...connectors import (
    FinancialConnector,
)

from .authentication import (
    SwiftAuthentication,
    SwiftAuthenticationConfiguration,
)

from .icr_client import (
    InstantCashReportingClient,
    InstantCashReportingConfiguration,
)

from .payments_client import (
    PaymentsClient,
    PaymentsConfiguration,
)

from .kyc_client import (
    KYCClient,
    KYCConfiguration,
)

from .compliance_client import (
    ComplianceClient,
    ComplianceConfiguration,
)

from .constants import (
    PROVIDER_NAME,
    PROVIDER_DISPLAY_NAME,
    PROVIDER_VENDOR,
    PROVIDER_VERSION,
    SWIFT_MESSAGE_DEFINITIONS,
)

from .protocol_registry import (
    protocol_registry,
)

from .handlers import (

    MT103Handler,

    MT202Handler,

    MT700Handler,

    MT707Handler,

    MT710Handler,

    MT720Handler,

    MT742Handler,

    MT747Handler,

    MT750Handler,

    MT752Handler,

    MT754Handler,

    MT756Handler,

    MT760Handler,

    MT767Handler,

    MT799Handler,

    MT940Handler,

    MXHandler,

)

from ...normalizer import (
    financial_evidence_normalizer,
)

from ...replay.fixture_loader import FixtureLoader
from ...replay.replay_engine import ReplayEngine

from .fin.validator import FINValidator


# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class SwiftConfiguration:
    """
    Canonical SWIFT configuration.
    """

    token_url: str

    client_id: str

    client_secret: str

    api_base_url: str

    timeout: int = 30

    replay_enabled: bool = False

    replay_dataset: str = "MT103"

    fixtures_directory: str | None = None


# ============================================================================
# Adapter
# ============================================================================


class SwiftAdapter(FinancialAdapter):
    """
    Canonical SWIFT Financial Adapter.
    """

    def __init__(
        self,
        connector: FinancialConnector,
        configuration: SwiftConfiguration,
    ) -> None:

        super().__init__(connector)

        authentication = SwiftAuthentication(

            SwiftAuthenticationConfiguration(

                token_url=configuration.token_url,

                client_id=configuration.client_id,

                client_secret=configuration.client_secret,

                timeout=configuration.timeout,
            )
        )

        self.authentication = authentication

        self.icr = InstantCashReportingClient(

            InstantCashReportingConfiguration(

                base_url=configuration.api_base_url,

                timeout=configuration.timeout,
            ),

            authentication,
        )

        self.payments = PaymentsClient(

            PaymentsConfiguration(

                base_url=configuration.api_base_url,

                timeout=configuration.timeout,
            ),

            authentication,
        )

        self.kyc = KYCClient(

            KYCConfiguration(

                base_url=configuration.api_base_url,

                timeout=configuration.timeout,
            ),

            authentication,
        )

        self.compliance = ComplianceClient(

            ComplianceConfiguration(

                base_url=configuration.api_base_url,

                timeout=configuration.timeout,
            ),

            authentication,
        )

        self.configuration = configuration

        self.replay_enabled = configuration.replay_enabled

        self.replay_engine = None

        # --------------------------------------------------------------
        # Canonical SWIFT Protocol Registry
        # --------------------------------------------------------------

        protocol_registry.register(
            MT103Handler(),
        )

        protocol_registry.register(
            MT202Handler(),
        )

        protocol_registry.register(
            MT700Handler(),
        )

        protocol_registry.register(
            MT707Handler(),
        )

        protocol_registry.register(
            MT710Handler(),
        )

        protocol_registry.register(
            MT720Handler(),
        )

        protocol_registry.register(
            MT742Handler(),
        )

        protocol_registry.register(
            MT747Handler(),
        )

        protocol_registry.register(
            MT750Handler(),
        )

        protocol_registry.register(
            MT752Handler(),
        )

        protocol_registry.register(
            MT754Handler(),
        )

        protocol_registry.register(
            MT756Handler(),
        )

        protocol_registry.register(
            MT760Handler(),
        )

        protocol_registry.register(
            MT767Handler(),
        )

        protocol_registry.register(
            MT799Handler(),
        )

        protocol_registry.register(
            MT940Handler(),
        )

        protocol_registry.register(
            MXHandler(),
        )

        if (
            configuration.replay_enabled
            and configuration.fixtures_directory
        ):

            loader = FixtureLoader(
                configuration.fixtures_directory,
            )

            self.replay_engine = ReplayEngine(
                loader,
            )


    # ------------------------------------------------------------------
    # Provider Metadata
    # ------------------------------------------------------------------

    def descriptor(
        self,
    ) -> ProviderDescriptor:

        return ProviderDescriptor(

            name=PROVIDER_NAME,

            display_name=PROVIDER_DISPLAY_NAME,

            vendor=PROVIDER_VENDOR,

            version=PROVIDER_VERSION,

            description=(
                "SWIFT Financial Infrastructure"
            ),
        )

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capability(
        self,
    ) -> ProviderCapability:

        return ProviderCapability(

            streaming=False,

            historical_sync=True,

            incremental_sync=True,

            batch_sync=True,

            authentication="OAuth2",
        )

    # ------------------------------------------------------------------
    # Infrastructure Builders
    # ------------------------------------------------------------------

    def _build_institution(self):

        return self.icr.institution()


    def _build_account(self):

        return self.icr.account()


    # ------------------------------------------------------------------
    # Financial Builders
    # ------------------------------------------------------------------

    def _build_cash_balances(self):

        return self.icr.cash_balances()


    def _build_cash_transfers(self):

        return self.payments.cash_transfers()


    def _build_settlement_instructions(self):

        return self.payments.settlement_instructions()


    def _build_settlement_confirmations(self):

        return self.payments.settlement_confirmations()


    def _build_custody_holdings(self):

        return self.icr.custody_holdings()


    def _build_funding_events(self):

        return self.icr.funding_events()


    def _build_corporate_actions(self):

        return self.icr.corporate_actions()


    def _build_bank_statements(self):

        return self.icr.bank_statements()


    def _build_letters_of_credit(self):

        return self.compliance.letters_of_credit()


    def _build_bank_guarantees(self):

        return self.compliance.bank_guarantees()


    def _build_collateral(self):

        return self.icr.collateral()


    def _build_margin(self):

        return self.icr.margin()


    def _build_payments(self):

        return self.payments.payments()

    # ------------------------------------------------------------------
    # Acquisition
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Replay Acquisition
    # ------------------------------------------------------------------

    def acquire_replay(
        self,
    ):

        if self.replay_engine is None:

            raise RuntimeError(
                "Replay Engine is not configured."
            )

        if not self.configuration.replay_dataset:

            raise RuntimeError(
                "Replay dataset has not been configured."
            )

        return self.replay_engine.replay(
            self.configuration.replay_dataset,
            self._process_fixture,
        )

    def _process_fixture(
        self,
        fixture,
    ):
        """
        Process one replay fixture through the
        canonical FIN acquisition pipeline.
        """

        from .fin.block_parser import (
            FINBlockParser,
        )

        from .fin.field_parser import (
            FINFieldParser,
        )

        from .fin.validator import (
            FINValidator,
        )

        parser = FINBlockParser()

        message = parser.parse(
            fixture.contents,
        )

        if message.text is None:

            raise ValueError(
                "Replay fixture does not contain FIN Block 4."
            )

        fields = FINFieldParser().parse(
            message.text.text,
        )

        result = self._dispatch_message(
            message,
            fields,
        )

        result["dataset"] = fixture.dataset

        result["fixture"] = fixture.path.name

        return result

    # ------------------------------------------------------------------
    # Message Dispatch
    # ------------------------------------------------------------------

    def _dispatch_message(
        self,
        message,
        fields,
    ):

        message_type = message.message_type

        if message_type is None:

            raise ValueError(
                "Unable to determine SWIFT message type."
            )

        handler = protocol_registry.handler(
            message_type,
        )

        if handler is None:

            raise NotImplementedError(

                f"Unsupported SWIFT protocol "

                f"MT{message_type}."

            )

        return handler.process(

            self,

            message,

            fields,

        )


    def acquire(
        self,
    ):
        """
        Acquire the complete SWIFT evidence surface.

        The returned payload follows the canonical Financial
        Infrastructure Engine acquisition contract.
        """

        if self.replay_enabled:

            replay_session = self.acquire_replay()

            return financial_evidence_normalizer.normalize(
                {
                    "connector_name": PROVIDER_NAME,
                    "connector_version": PROVIDER_VERSION,
                    "schema_version": "1.0",
                    "replay_session": replay_session,
                }
            )

        started = self.begin_sync()

        successful = False

        payload = {}

        try:

            institution = self._build_institution()

            account = self._build_account()

            cash_balances = self._build_cash_balances()

            cash_transfers = self._build_cash_transfers()

            settlement_instructions = (
                self._build_settlement_instructions()
            )

            settlement_confirmations = (
                self._build_settlement_confirmations()
            )

            custody_holdings = (
                self._build_custody_holdings()
            )

            funding_events = (
                self._build_funding_events()
            )

            corporate_actions = (
                self._build_corporate_actions()
            )

            bank_statements = (
                self._build_bank_statements()
            )

            letters_of_credit = (
                self._build_letters_of_credit()
            )

            bank_guarantees = (
                self._build_bank_guarantees()
            )

            collateral = (
                self._build_collateral()
            )

            margin = (
                self._build_margin()
            )

            payments = (
                self._build_payments()
            )

            payload = {

                # ------------------------------------------------------
                # Connector Metadata
                # ------------------------------------------------------

                "connector_name": PROVIDER_NAME,

                "connector_version": PROVIDER_VERSION,

                "schema_version": "1.0",

                # ------------------------------------------------------
                # Infrastructure
                # ------------------------------------------------------

                "institution": institution,

                "account": account,

                # ------------------------------------------------------
                # Financial Evidence
                # ------------------------------------------------------

                "cash_balances": cash_balances,

                "cash_transfers": cash_transfers,

                "settlement_instructions": settlement_instructions,

                "settlement_confirmations": settlement_confirmations,

                "custody_holdings": custody_holdings,

                "funding_events": funding_events,

                "corporate_actions": corporate_actions,

                "bank_statements": bank_statements,

                "letters_of_credit": letters_of_credit,

                "bank_guarantees": bank_guarantees,

                "collateral": collateral,

                "margin": margin,

                "payments": payments,
            }

            successful = True

            return financial_evidence_normalizer.normalize(
                payload,
            )

        finally:

            acquired = 0

            for value in payload.values():

                if isinstance(
                    value,
                    list,
                ):
                    acquired += len(value)

                elif value is not None:
                    acquired += 1

            self.finish_sync(

                started_at=started,

                acquired=acquired,

                successful=successful,
            )


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "SwiftConfiguration",

    "SwiftAdapter",
]