"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Canonical Evidence Models

This module defines the institutional evidence contracts used by every
financial infrastructure provider supported by TTL.

Providers include (but are not limited to):

- SWIFT
- MT760
- MT799
- Prime Brokers
- Custodians
- Commercial Banks
- Settlement Systems
- Treasury Platforms
- Payment Networks

No provider-specific objects should exist inside this module.

Every financial infrastructure provider must translate its native
objects into these canonical evidence models before evidence is
consumed elsewhere inside Trading Truth Layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from decimal import Decimal

from enum import Enum

from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from uuid import uuid4


# =============================================================================
# Engine Metadata
# =============================================================================


ENGINE_NAME = "financial_engine"
ENGINE_VERSION = "1.0.0"


# =============================================================================
# Supported Providers
# =============================================================================


class FinancialProvider(str, Enum):
    """Supported financial infrastructure providers."""

    SWIFT = "swift"
    MT760 = "mt760"
    MT799 = "mt799"

    BANK = "bank"

    PRIME_BROKER = "prime_broker"

    CUSTODIAN = "custodian"

    SETTLEMENT = "settlement"

    TREASURY = "treasury"

    PAYMENT = "payment"


# =============================================================================
# Evidence Categories
# =============================================================================


class FinancialEvidenceType(str, Enum):
    """Canonical evidence families."""

    CASH_BALANCE = "cash_balance"

    CASH_TRANSFER = "cash_transfer"

    SETTLEMENT_INSTRUCTION = "settlement_instruction"

    SETTLEMENT_CONFIRMATION = "settlement_confirmation"

    CUSTODY_HOLDING = "custody_holding"

    FUNDING_EVENT = "funding_event"

    CORPORATE_ACTION = "corporate_action"

    BANK_STATEMENT = "bank_statement"

    LETTER_OF_CREDIT = "letter_of_credit"

    BANK_GUARANTEE = "bank_guarantee"

    COLLATERAL = "collateral"

    MARGIN = "margin"

    PAYMENT = "payment"


# =============================================================================
# Synchronization Status
# =============================================================================


class SynchronizationStatus(str, Enum):

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    PARTIAL = "partial"

    FAILED = "failed"

    CANCELLED = "cancelled"


# =============================================================================
# Financial Account Types
# =============================================================================


class FinancialAccountType(str, Enum):

    CURRENT = "current"

    SAVINGS = "savings"

    CUSTODY = "custody"

    SETTLEMENT = "settlement"

    TREASURY = "treasury"

    MARGIN = "margin"

    COLLATERAL = "collateral"

    PRIME_BROKER = "prime_broker"


# =============================================================================
# Currency
# =============================================================================


@dataclass(slots=True)
class Currency:

    code: str

    numeric_code: Optional[str] = None

    symbol: Optional[str] = None

    name: Optional[str] = None


# =============================================================================
# Financial Institution
# =============================================================================


@dataclass(slots=True)
class FinancialInstitution:

    institution_id: str

    provider: FinancialProvider

    legal_name: str

    bic: Optional[str] = None

    lei: Optional[str] = None

    country: Optional[str] = None

    regulator: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Counterparty
# =============================================================================


@dataclass(slots=True)
class Counterparty:

    counterparty_id: str

    legal_name: str

    bic: Optional[str] = None

    lei: Optional[str] = None

    country: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Financial Account
# =============================================================================


@dataclass(slots=True)
class FinancialAccount:

    account_id: str

    institution: FinancialInstitution

    account_number: str

    account_name: str

    account_type: FinancialAccountType

    currency: Currency

    opened_at: Optional[datetime] = None

    closed_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Canonical Evidence Base
# =============================================================================


@dataclass(slots=True)
class FinancialEvidence:

    evidence_id: str = field(default_factory=lambda: str(uuid4()))

    provider: FinancialProvider = FinancialProvider.BANK

    evidence_type: FinancialEvidenceType = (
        FinancialEvidenceType.CASH_BALANCE
    )

    acquired_at: datetime = field(default_factory=datetime.utcnow)

    synchronized_at: Optional[datetime] = None

    account: Optional[FinancialAccount] = None

    source_reference: Optional[str] = None

    checksum: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Cash Balance Evidence
# =============================================================================


@dataclass(slots=True)
class CashBalanceEvidence(FinancialEvidence):
    """Canonical cash balance evidence."""

    available_balance: Decimal = Decimal("0")

    ledger_balance: Decimal = Decimal("0")

    booked_balance: Decimal = Decimal("0")

    pending_balance: Decimal = Decimal("0")

    currency: Optional[Currency] = None

    value_date: Optional[datetime] = None


# =============================================================================
# Cash Transfer Evidence
# =============================================================================


@dataclass(slots=True)
class CashTransferEvidence(FinancialEvidence):
    """Canonical cash movement evidence."""

    transfer_reference: str = ""

    sender: Optional[Counterparty] = None

    receiver: Optional[Counterparty] = None

    amount: Decimal = Decimal("0")

    currency: Optional[Currency] = None

    transfer_type: Optional[str] = None

    status: Optional[str] = None

    initiated_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None


# =============================================================================
# Settlement Instruction Evidence
# =============================================================================


@dataclass(slots=True)
class SettlementInstructionEvidence(FinancialEvidence):
    """Settlement instruction received from an institution."""

    instruction_id: str = ""

    trade_reference: Optional[str] = None

    settlement_date: Optional[datetime] = None

    settlement_amount: Decimal = Decimal("0")

    currency: Optional[Currency] = None

    delivering_party: Optional[Counterparty] = None

    receiving_party: Optional[Counterparty] = None

    instruction_status: Optional[str] = None


# =============================================================================
# Settlement Confirmation Evidence
# =============================================================================


@dataclass(slots=True)
class SettlementConfirmationEvidence(FinancialEvidence):
    """Settlement completion confirmation."""

    confirmation_id: str = ""

    instruction_reference: Optional[str] = None

    settled_amount: Decimal = Decimal("0")

    currency: Optional[Currency] = None

    settled_at: Optional[datetime] = None

    settlement_status: Optional[str] = None

    settlement_location: Optional[str] = None


# =============================================================================
# Custody Holding Evidence
# =============================================================================


@dataclass(slots=True)
class CustodyHoldingEvidence(FinancialEvidence):
    """Custodian asset holding."""

    security_id: str = ""

    isin: Optional[str] = None

    cusip: Optional[str] = None

    ticker: Optional[str] = None

    asset_name: Optional[str] = None

    asset_type: Optional[str] = None

    quantity: Decimal = Decimal("0")

    market_value: Decimal = Decimal("0")

    currency: Optional[Currency] = None

    valuation_date: Optional[datetime] = None


# =============================================================================
# Funding Event Evidence
# =============================================================================


@dataclass(slots=True)
class FundingEventEvidence(FinancialEvidence):
    """Prime broker or bank funding event."""

    funding_reference: str = ""

    funding_type: Optional[str] = None

    amount: Decimal = Decimal("0")

    currency: Optional[Currency] = None

    counterparty: Optional[Counterparty] = None

    event_time: Optional[datetime] = None

    maturity_date: Optional[datetime] = None


# =============================================================================
# Corporate Action Evidence
# =============================================================================


@dataclass(slots=True)
class CorporateActionEvidence(FinancialEvidence):
    """Corporate action received from custodian."""

    corporate_action_id: str = ""

    action_type: Optional[str] = None

    security_id: Optional[str] = None

    isin: Optional[str] = None

    announcement_date: Optional[datetime] = None

    effective_date: Optional[datetime] = None

    payable_date: Optional[datetime] = None

    amount: Optional[Decimal] = None

    currency: Optional[Currency] = None


# =============================================================================
# Bank Statement Evidence
# =============================================================================


@dataclass(slots=True)
class BankStatementEvidence(FinancialEvidence):
    """Bank statement metadata."""

    statement_reference: str = ""

    statement_number: Optional[str] = None

    period_start: Optional[datetime] = None

    period_end: Optional[datetime] = None

    opening_balance: Decimal = Decimal("0")

    closing_balance: Decimal = Decimal("0")

    currency: Optional[Currency] = None


# =============================================================================
# Letter of Credit Evidence
# =============================================================================


@dataclass(slots=True)
class LetterOfCreditEvidence(FinancialEvidence):
    """Canonical Letter of Credit (LC)."""

    lc_reference: str = ""

    applicant: Optional[Counterparty] = None

    beneficiary: Optional[Counterparty] = None

    issuing_bank: Optional[FinancialInstitution] = None

    advising_bank: Optional[FinancialInstitution] = None

    amount: Decimal = Decimal("0")

    currency: Optional[Currency] = None

    expiry_date: Optional[datetime] = None

    issue_date: Optional[datetime] = None


# =============================================================================
# Bank Guarantee Evidence
# =============================================================================


@dataclass(slots=True)
class BankGuaranteeEvidence(FinancialEvidence):
    """Canonical MT760 / bank guarantee evidence."""

    guarantee_reference: str = ""

    guarantor: Optional[FinancialInstitution] = None

    beneficiary: Optional[Counterparty] = None

    applicant: Optional[Counterparty] = None

    guarantee_amount: Decimal = Decimal("0")

    currency: Optional[Currency] = None

    issue_date: Optional[datetime] = None

    expiry_date: Optional[datetime] = None

    guarantee_status: Optional[str] = None


# =============================================================================
# Collateral Evidence
# =============================================================================


@dataclass(slots=True)
class CollateralEvidence(FinancialEvidence):
    """Collateral posted or received."""

    collateral_id: str = ""

    collateral_type: Optional[str] = None

    asset_identifier: Optional[str] = None

    quantity: Decimal = Decimal("0")

    market_value: Decimal = Decimal("0")

    haircut: Optional[Decimal] = None

    currency: Optional[Currency] = None

    counterparty: Optional[Counterparty] = None

    valuation_date: Optional[datetime] = None


# =============================================================================
# Margin Evidence
# =============================================================================


@dataclass(slots=True)
class MarginEvidence(FinancialEvidence):
    """Initial / Variation margin evidence."""

    margin_id: str = ""

    margin_type: Optional[str] = None

    required_margin: Decimal = Decimal("0")

    posted_margin: Decimal = Decimal("0")

    excess_margin: Decimal = Decimal("0")

    currency: Optional[Currency] = None

    valuation_date: Optional[datetime] = None


# =============================================================================
# Payment Evidence
# =============================================================================


@dataclass(slots=True)
class PaymentEvidence(FinancialEvidence):
    """Canonical payment instruction."""

    payment_reference: str = ""

    payment_method: Optional[str] = None

    payer: Optional[Counterparty] = None

    beneficiary: Optional[Counterparty] = None

    amount: Decimal = Decimal("0")

    currency: Optional[Currency] = None

    execution_date: Optional[datetime] = None

    payment_status: Optional[str] = None


# =============================================================================
# Synchronization Statistics
# =============================================================================


@dataclass(slots=True)
class SynchronizationStatistics:
    """Statistics produced during synchronization."""

    total_received: int = 0

    total_validated: int = 0

    total_translated: int = 0

    total_registered: int = 0

    total_published: int = 0

    duplicates_removed: int = 0

    validation_failures: int = 0

    translation_failures: int = 0

    synchronization_failures: int = 0


# =============================================================================
# Synchronization Result
# =============================================================================


@dataclass(slots=True)
class SynchronizationResult:
    """Canonical synchronization result."""

    synchronization_id: str = field(default_factory=lambda: str(uuid4()))

    provider: FinancialProvider = FinancialProvider.BANK

    started_at: datetime = field(default_factory=datetime.utcnow)

    completed_at: Optional[datetime] = None

    status: SynchronizationStatus = SynchronizationStatus.PENDING

    statistics: SynchronizationStatistics = field(
        default_factory=SynchronizationStatistics
    )

    messages: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Registry Metadata
# =============================================================================


@dataclass(slots=True)
class RegistryMetadata:
    """Evidence registry metadata."""

    registry_id: str = field(default_factory=lambda: str(uuid4()))

    registered_at: datetime = field(default_factory=datetime.utcnow)

    registry_version: str = "1.0"

    canonical_hash: Optional[str] = None

    registry_state: str = "registered"


# =============================================================================
# Provenance Metadata
# =============================================================================


@dataclass(slots=True)
class ProvenanceMetadata:
    """Evidence provenance."""

    acquisition_time: datetime = field(default_factory=datetime.utcnow)

    provider: Optional[FinancialProvider] = None

    provider_reference: Optional[str] = None

    source_system: Optional[str] = None

    acquisition_method: Optional[str] = None

    acquisition_node: Optional[str] = None

    checksum: Optional[str] = None

    signature: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Publication Metadata
# =============================================================================


@dataclass(slots=True)
class PublicationMetadata:
    """Publisher metadata."""

    published: bool = False

    published_at: Optional[datetime] = None

    publisher: Optional[str] = None

    publication_reference: Optional[str] = None

    publication_version: str = "1.0"

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Canonical Evidence Envelope
# =============================================================================


@dataclass(slots=True)
class CanonicalFinancialEvidence:
    """
    Final canonical evidence emitted by the Financial Engine.
    """

    evidence: FinancialEvidence

    registry: RegistryMetadata

    provenance: ProvenanceMetadata

    publication: PublicationMetadata

    synchronized: bool = False

    synchronized_at: Optional[datetime] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Synchronization Batch
# =============================================================================


@dataclass(slots=True)
class FinancialSynchronizationBatch:
    """
    Collection of canonical financial evidence synchronized
    during a single acquisition cycle.
    """

    batch_id: str = field(default_factory=lambda: str(uuid4()))

    provider: FinancialProvider = FinancialProvider.BANK

    started_at: datetime = field(default_factory=datetime.utcnow)

    completed_at: Optional[datetime] = None

    evidences: List[CanonicalFinancialEvidence] = field(default_factory=list)

    result: Optional[SynchronizationResult] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Provider Capability
# =============================================================================


@dataclass(slots=True)
class ProviderCapability:
    """
    Declares the capabilities supported by a financial infrastructure provider.
    """

    provider: FinancialProvider

    supports_cash_balances: bool = False

    supports_cash_transfers: bool = False

    supports_settlement_instructions: bool = False

    supports_settlement_confirmations: bool = False

    supports_custody_holdings: bool = False

    supports_funding_events: bool = False

    supports_corporate_actions: bool = False

    supports_bank_statements: bool = False

    supports_letters_of_credit: bool = False

    supports_bank_guarantees: bool = False

    supports_collateral: bool = False

    supports_margin: bool = False

    supports_payments: bool = False

    supports_incremental_sync: bool = True

    supports_historical_sync: bool = True

    supports_real_time_sync: bool = False

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Engine Configuration
# =============================================================================


@dataclass(slots=True)
class FinancialEngineConfiguration:
    """
    Runtime configuration for the Financial Engine.
    """

    enabled: bool = True

    engine_name: str = ENGINE_NAME

    engine_version: str = ENGINE_VERSION

    max_parallel_synchronizations: int = 5

    deduplication_enabled: bool = True

    provenance_enabled: bool = True

    registry_enabled: bool = True

    publisher_enabled: bool = True

    validate_before_translation: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Engine Health
# =============================================================================


@dataclass(slots=True)
class FinancialEngineHealth:
    """
    Overall Financial Engine health.
    """

    engine_name: str = ENGINE_NAME

    healthy: bool = True

    started_at: Optional[datetime] = None

    last_synchronization: Optional[datetime] = None

    registered_providers: int = 0

    active_connections: int = 0

    synchronization_queue: int = 0

    failed_synchronizations: int = 0

    published_evidence: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Provider Registration
# =============================================================================


@dataclass(slots=True)
class FinancialProviderRegistration:
    """
    Provider registration information maintained by the engine.
    """

    provider: FinancialProvider

    institution: Optional[FinancialInstitution] = None

    capability: Optional[ProviderCapability] = None

    enabled: bool = True

    registered_at: datetime = field(default_factory=datetime.utcnow)

    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Engine Snapshot
# =============================================================================


@dataclass(slots=True)
class FinancialEngineSnapshot:
    """
    Operational snapshot of the Financial Engine.
    """

    generated_at: datetime = field(default_factory=datetime.utcnow)

    configuration: FinancialEngineConfiguration = field(
        default_factory=FinancialEngineConfiguration
    )

    health: FinancialEngineHealth = field(
        default_factory=FinancialEngineHealth
    )

    providers: List[FinancialProviderRegistration] = field(
        default_factory=list
    )

    synchronizations: List[SynchronizationResult] = field(
        default_factory=list
    )


# ============================================================================
# Financial Evidence Package
# ============================================================================

@dataclass(slots=True)
class FinancialEvidencePackage:
    """
    Canonical acquisition package produced by the Financial Translator.

    This package represents one provider synchronization before
    validation and synchronization.
    """

    institution: Optional[FinancialInstitution] = None

    account: Optional[FinancialAccount] = None

    cash_balances: List[CashBalanceEvidence] = field(default_factory=list)

    cash_transfers: List[CashTransferEvidence] = field(default_factory=list)

    settlement_instructions: List[SettlementInstructionEvidence] = field(default_factory=list)

    settlement_confirmations: List[SettlementConfirmationEvidence] = field(default_factory=list)

    custody_holdings: List[CustodyHoldingEvidence] = field(default_factory=list)

    funding_events: List[FundingEventEvidence] = field(default_factory=list)

    corporate_actions: List[CorporateActionEvidence] = field(default_factory=list)

    bank_statements: List[BankStatementEvidence] = field(default_factory=list)

    letters_of_credit: List[LetterOfCreditEvidence] = field(default_factory=list)

    bank_guarantees: List[BankGuaranteeEvidence] = field(default_factory=list)

    collateral: List[CollateralEvidence] = field(default_factory=list)

    margin: List[MarginEvidence] = field(default_factory=list)

    payments: List[PaymentEvidence] = field(default_factory=list)


# =============================================================================
# Public Exports
# =============================================================================


__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "FinancialProvider",
    "FinancialEvidenceType",
    "SynchronizationStatus",
    "FinancialAccountType",
    "Currency",
    "FinancialInstitution",
    "Counterparty",
    "FinancialAccount",
    "FinancialEvidence",
    "CashBalanceEvidence",
    "CashTransferEvidence",
    "SettlementInstructionEvidence",
    "SettlementConfirmationEvidence",
    "CustodyHoldingEvidence",
    "FundingEventEvidence",
    "CorporateActionEvidence",
    "BankStatementEvidence",
    "LetterOfCreditEvidence",
    "BankGuaranteeEvidence",
    "CollateralEvidence",
    "MarginEvidence",
    "PaymentEvidence",
    "SynchronizationStatistics",
    "SynchronizationResult",
    "RegistryMetadata",
    "ProvenanceMetadata",
    "PublicationMetadata",
    "CanonicalFinancialEvidence",
    "FinancialSynchronizationBatch",
    "ProviderCapability",
    "FinancialEngineConfiguration",
    "FinancialEngineHealth",
    "FinancialProviderRegistration",
    "FinancialEngineSnapshot",
    "FinancialEvidencePackage",
]