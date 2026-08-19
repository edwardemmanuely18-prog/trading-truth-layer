"""
Trading Truth Layer
Canonical Evidence Schema

This module defines the broker-neutral institutional evidence contract.

Rules
-----
1. Pure domain objects only.
2. No SQLAlchemy dependencies.
3. No provider SDK dependencies.
4. No MT5 / IBKR / cTrader specific types.
5. Provider-specific data is translated into these objects.
6. Provenance and lineage are first-class.
7. Canonical evidence is the institutional data contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ============================================================================
# Enumerations
# ============================================================================


class EvidenceType(str, Enum):
    ACCOUNT = "account"
    BALANCE = "balance"
    POSITION = "position"
    ORDER = "order"
    EXECUTION = "execution"
    TRADE = "trade"
    MARGIN = "margin"
    PORTFOLIO = "portfolio"
    MARKET = "market"
    TERMINAL = "terminal"
    RISK = "risk"
    STATEMENT = "statement"
    DOCUMENT = "document"
    GOVERNANCE = "governance"
    SYNCHRONIZATION = "synchronization"
    VERIFICATION = "verification"
    OTHER = "other"


class EvidenceSource(str, Enum):
    API = "api"
    FIX = "fix"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    REST = "rest"
    OPENAPI = "openapi"
    SDK = "sdk"
    DESKTOP = "desktop"
    IMPORT = "import"
    MANUAL = "manual"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class ProvenanceLevel(str, Enum):
    VERIFIED = "verified"
    DIRECT = "direct"
    DERIVED = "derived"
    IMPORTED = "imported"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class SynchronizationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


# ============================================================================
# Identity
# ============================================================================


@dataclass(slots=True)
class EvidenceIdentity:
    """
    Stable identity for one canonical evidence object.
    """

    evidence_id: str

    workspace_id: int | None = None

    evidence_type: EvidenceType = EvidenceType.OTHER

    provider_name: str | None = None
    provider_type: str | None = None

    account_id: str | None = None

    native_identifier: str | None = None


# ============================================================================
# Provider
# ============================================================================


@dataclass(slots=True)
class ProviderInformation:
    """
    Broker/provider-neutral source information.
    """

    provider_name: str | None = None
    provider_type: str | None = None

    platform_name: str | None = None
    platform_version: str | None = None

    broker_server: str | None = None
    broker_account_id: str | None = None
    broker_account_name: str | None = None

    account_currency: str | None = None

    provider_account_key: str | None = None


# ============================================================================
# Provenance
# ============================================================================


@dataclass(slots=True)
class ProvenanceRecord:
    """
    Institutional provenance of canonical evidence.
    """

    level: ProvenanceLevel = ProvenanceLevel.UNKNOWN

    source: EvidenceSource = EvidenceSource.UNKNOWN

    connector_name: str | None = None
    connector_version: str | None = None

    translator_name: str | None = None
    translator_version: str | None = None

    native_identifier: str | None = None
    native_object_type: str | None = None
    raw_identifier: str | None = None

    checksum: str | None = None

    confidence: float = 1.0

    notes: str | None = None


# ============================================================================
# Lineage
# ============================================================================


@dataclass(slots=True)
class LineageRecord:
    """
    Describes how canonical evidence relates to source evidence.
    """

    source_evidence_id: str | None = None

    parent_evidence_ids: list[str] = field(
        default_factory=list
    )

    derived_from: list[str] = field(
        default_factory=list
    )

    transformation: str | None = None

    transformation_version: str | None = None


# ============================================================================
# Integrity
# ============================================================================


@dataclass(slots=True)
class IntegrityRecord:
    """
    Cryptographic and structural integrity state.
    """

    content_hash: str | None = None

    canonical_hash: str | None = None

    algorithm: str = "sha256"

    verified: bool = False

    immutable: bool = False

    integrity_status: str = "unknown"


# ============================================================================
# Chain of Custody
# ============================================================================


@dataclass(slots=True)
class ChainOfCustodyRecord:
    """
    Institutional evidence custody history.
    """

    events: list[str] = field(
        default_factory=list
    )

    acquired_at: datetime | None = None

    received_at: datetime | None = None

    canonicalized_at: datetime | None = None

    verified_at: datetime | None = None


# ============================================================================
# Synchronization
# ============================================================================


@dataclass(slots=True)
class SynchronizationRecord:
    """
    Synchronization lifecycle metadata.
    """

    synchronization_id: str | None = None

    synchronization_status: SynchronizationStatus = (
        SynchronizationStatus.PENDING
    )

    synchronization_method: str | None = None

    synchronized_at: datetime | None = None

    sequence: int | None = None


# ============================================================================
# Account
# ============================================================================


@dataclass(slots=True)
class AccountEvidence:
    account_id: str | None = None
    account_number: str | None = None

    account_name: str | None = None

    account_type: str | None = None
    account_state: str | None = None

    currency: str | None = None

    broker: str | None = None
    server: str | None = None


# ============================================================================
# Instrument
# ============================================================================


@dataclass(slots=True)
class InstrumentEvidence:
    symbol: str | None = None

    asset_class: str | None = None

    exchange: str | None = None

    market: str | None = None

    currency: str | None = None


# ============================================================================
# Position
# ============================================================================


@dataclass(slots=True)
class PositionEvidence:
    position_id: str | None = None

    broker_position_id: str | None = None

    account_id: str | None = None

    symbol: str | None = None

    side: str | None = None

    quantity: float | None = None

    open_price: float | None = None
    current_price: float | None = None
    average_price: float | None = None

    stop_loss: float | None = None
    take_profit: float | None = None

    unrealized_pnl: float | None = None
    realized_pnl: float | None = None

    margin_used: float | None = None
    exposure: float | None = None

    opened_at: datetime | None = None
    updated_at: datetime | None = None
    closed_at: datetime | None = None


# ============================================================================
# Order
# ============================================================================


@dataclass(slots=True)
class OrderEvidence:
    order_id: str | None = None

    broker_order_id: str | None = None

    account_id: str | None = None

    symbol: str | None = None

    side: str | None = None

    order_type: str | None = None

    quantity: float | None = None

    requested_price: float | None = None
    executed_price: float | None = None

    status: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None


# ============================================================================
# Execution
# ============================================================================


@dataclass(slots=True)
class ExecutionEvidence:
    execution_id: str | None = None

    broker_execution_id: str | None = None

    order_id: str | None = None

    account_id: str | None = None

    symbol: str | None = None

    side: str | None = None

    quantity: float | None = None

    price: float | None = None

    commission: float | None = None
    fees: float | None = None

    executed_at: datetime | None = None


# ============================================================================
# Trade
# ============================================================================


@dataclass(slots=True)
class TradeEvidence:
    trade_id: str | None = None

    broker_trade_id: str | None = None

    account_id: str | None = None

    symbol: str | None = None

    side: str | None = None

    quantity: float | None = None

    entry_price: float | None = None
    exit_price: float | None = None

    opened_at: datetime | None = None
    closed_at: datetime | None = None

    gross_pnl: float | None = None
    net_pnl: float | None = None

    commission: float | None = None
    swap: float | None = None
    fees: float | None = None

    strategy_tag: str | None = None


# ============================================================================
# Balance
# ============================================================================


@dataclass(slots=True)
class BalanceEvidence:
    account_id: str | None = None

    currency: str | None = None

    balance: float | None = None

    equity: float | None = None

    available_margin: float | None = None

    used_margin: float | None = None

    free_margin: float | None = None

    captured_at: datetime | None = None


# ============================================================================
# Margin
# ============================================================================


@dataclass(slots=True)
class MarginEvidence:
    account_id: str | None = None

    currency: str | None = None

    initial_margin: float | None = None

    maintenance_margin: float | None = None

    used_margin: float | None = None

    available_margin: float | None = None

    margin_level: float | None = None

    captured_at: datetime | None = None


# ============================================================================
# Portfolio
# ============================================================================


@dataclass(slots=True)
class PortfolioEvidence:
    account_id: str | None = None

    balance: float | None = None
    equity: float | None = None

    cash: float | None = None

    gross_exposure: float | None = None
    net_exposure: float | None = None

    captured_at: datetime | None = None


# ============================================================================
# Market
# ============================================================================


@dataclass(slots=True)
class MarketEvidence:
    symbol: str | None = None

    bid: float | None = None
    ask: float | None = None
    last: float | None = None

    timestamp: datetime | None = None


# ============================================================================
# Terminal / System
# ============================================================================


@dataclass(slots=True)
class TerminalEvidence:
    terminal_name: str | None = None

    terminal_version: str | None = None

    operating_system: str | None = None

    server_name: str | None = None

    server_region: str | None = None

    connected: bool | None = None

    captured_at: datetime | None = None


# ============================================================================
# Risk
# ============================================================================


@dataclass(slots=True)
class RiskEvidence:
    account_id: str | None = None

    exposure: float | None = None

    exposure_percentage: float | None = None

    drawdown: float | None = None

    margin_utilization: float | None = None

    risk_percentage: float | None = None

    captured_at: datetime | None = None


# ============================================================================
# Canonical Evidence Record
# ============================================================================


@dataclass(slots=True)
class CanonicalEvidence:
    """
    Root institutional canonical evidence record.

    Every evidence object entering the TTL Evidence Registry must
    be representable through this contract.
    """

    identity: EvidenceIdentity

    provider: ProviderInformation

    provenance: ProvenanceRecord

    lineage: LineageRecord = field(
        default_factory=LineageRecord
    )

    integrity: IntegrityRecord = field(
        default_factory=IntegrityRecord
    )

    chain_of_custody: ChainOfCustodyRecord = field(
        default_factory=ChainOfCustodyRecord
    )

    synchronization: SynchronizationRecord = field(
        default_factory=SynchronizationRecord
    )

    account: AccountEvidence | None = None

    instrument: InstrumentEvidence | None = None

    position: PositionEvidence | None = None

    order: OrderEvidence | None = None

    execution: ExecutionEvidence | None = None

    trade: TradeEvidence | None = None

    balance: BalanceEvidence | None = None

    margin: MarginEvidence | None = None

    portfolio: PortfolioEvidence | None = None

    market: MarketEvidence | None = None

    terminal: TerminalEvidence | None = None

    risk: RiskEvidence | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )