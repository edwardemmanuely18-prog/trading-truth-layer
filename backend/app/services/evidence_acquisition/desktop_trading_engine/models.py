"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Desktop Trading Synchronization Engine

Canonical Evidence Models

This module defines the institutional evidence contracts used by every
desktop trading provider supported by TTL.

Providers include (but are not limited to):

- MetaTrader 4
- MetaTrader 5
- cTrader
- NinjaTrader
- TradeStation
- Sierra Chart
- CQG
- MultiCharts
- Quantower
- DXtrade
- MatchTrader

No provider-specific objects should exist inside this file.

Every connector must translate native provider objects into these
canonical evidence models before evidence is consumed elsewhere inside TTL.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


# ============================================================================
# Evidence Version
# ============================================================================

EVIDENCE_SCHEMA_VERSION = "1.0"


# ============================================================================
# Enumerations
# ============================================================================

class ProviderType(str, Enum):
    """Evidence provider category."""

    DESKTOP_TRADING = "desktop_trading"


class AccountState(str, Enum):
    """Trading account state."""

    LIVE = "live"

    DEMO = "demo"

    READ_ONLY = "read_only"

    SUSPENDED = "suspended"

    ARCHIVED = "archived"

    UNKNOWN = "unknown"


class ConnectionStatus(str, Enum):
    """Connection status."""

    CONNECTED = "connected"

    CONNECTING = "connecting"

    DISCONNECTED = "disconnected"

    FAILED = "failed"

    UNKNOWN = "unknown"


class SynchronizationStatus(str, Enum):
    """Synchronization lifecycle."""

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    PARTIAL = "partial"


class EvidenceSource(str, Enum):
    """How evidence was obtained."""

    API = "api"

    SDK = "sdk"

    TERMINAL = "terminal"

    FILE = "file"

    IMPORT = "import"

    MANUAL = "manual"

    UNKNOWN = "unknown"


class ProvenanceLevel(str, Enum):
    """
    Institutional evidence provenance.
    """

    VERIFIED = "verified"

    DIRECT = "direct"

    DERIVED = "derived"

    IMPORTED = "imported"

    MANUAL = "manual"

    UNKNOWN = "unknown"


class PlatformType(str, Enum):
    """Desktop trading platforms."""

    MT4 = "mt4"

    MT5 = "mt5"

    CTRADER = "ctrader"

    NINJATRADER = "ninjatrader"

    TRADESTATION = "tradestation"

    SIERRA_CHART = "sierra_chart"

    MULTICHARTS = "multicharts"

    CQG = "cqg"

    QUANTOWER = "quantower"

    DXTRADE = "dxtrade"

    MATCHTRADER = "matchtrader"

    UNKNOWN = "unknown"


# ============================================================================
# Identity
# ============================================================================

@dataclass(slots=True)
class EvidenceIdentity:
    """
    Canonical identity shared by every evidence object.

    This identity uniquely identifies a piece of evidence regardless
    of broker or trading platform.
    """

    evidence_id: str = field(default_factory=lambda: str(uuid4()))

    workspace_id: Optional[int] = None

    provider_name: str = ""

    provider_type: ProviderType = ProviderType.DESKTOP_TRADING

    platform_name: PlatformType = PlatformType.UNKNOWN

    platform_version: Optional[str] = None

    account_id: Optional[str] = None

    account_number: Optional[str] = None

    account_state: AccountState = AccountState.UNKNOWN

    server_name: Optional[str] = None

    server_region: Optional[str] = None

    provider_account_key: Optional[str] = None

    workspace_slug: Optional[str] = None

    organization_id: Optional[str] = None


# ============================================================================
# Metadata
# ============================================================================

@dataclass(slots=True)
class EvidenceMetadata:
    """
    Operational metadata describing synchronization.
    """

    synchronization_id: Optional[str] = None

    synchronization_status: SynchronizationStatus = (
        SynchronizationStatus.PENDING
    )

    synchronized_at: Optional[datetime] = None

    captured_at: datetime = field(default_factory=datetime.utcnow)

    evidence_version: str = EVIDENCE_SCHEMA_VERSION

    source: EvidenceSource = EvidenceSource.UNKNOWN

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Provenance
# ============================================================================

@dataclass(slots=True)
class EvidenceProvenance:
    """
    Institutional provenance describing the origin and trustworthiness
    of evidence.
    """

    provenance_level: ProvenanceLevel = ProvenanceLevel.UNKNOWN

    connector_name: Optional[str] = None

    connector_version: Optional[str] = None

    translator_name: Optional[str] = None

    translator_version: Optional[str] = None

    native_identifier: Optional[str] = None

    native_object_type: Optional[str] = None

    raw_identifier: Optional[str] = None

    checksum: Optional[str] = None

    confidence: float = 1.0

    notes: Optional[str] = None


# ============================================================================
# Base Evidence
# ============================================================================

@dataclass(slots=True)
class Evidence:
    """
    Root institutional evidence object.

    Every canonical evidence model inside the Desktop Trading Engine
    inherits from this class.
    """

    identity: EvidenceIdentity = field(
        default_factory=EvidenceIdentity
    )

    metadata: EvidenceMetadata = field(
        default_factory=EvidenceMetadata
    )

    provenance: EvidenceProvenance = field(
        default_factory=EvidenceProvenance
    )


# ============================================================================
# Infrastructure Evidence
# ============================================================================

@dataclass(slots=True)
class InfrastructureEvidence(Evidence):
    """
    Base class for infrastructure evidence.

    Represents entities describing the trading environment rather than
    financial state.
    """

    active: bool = True


# ============================================================================
# Financial Evidence
# ============================================================================

@dataclass(slots=True)
class FinancialEvidence(Evidence):
    """
    Base class for all financial snapshot evidence.

    Every financial state synchronized from a desktop trading
    platform inherits these common fields.
    """

    account_id: Optional[str] = None

    currency: Optional[str] = None

    snapshot_time: Optional[datetime] = None


# ============================================================================
# Market Evidence
# ============================================================================

@dataclass(slots=True)
class MarketEvidence(Evidence):
    """
    Base class for all market-related evidence.
    """

    account_id: Optional[str] = None

    symbol: Optional[str] = None

    asset_class: Optional[str] = None

    exchange: Optional[str] = None

    market: Optional[str] = None


# ============================================================================
# Timestamped Evidence
# ============================================================================

@dataclass(slots=True)
class TimeStampedEvidence(MarketEvidence):
    """
    Base class for market evidence with lifecycle timestamps.
    """

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None

    closed_at: Optional[datetime] = None


# ============================================================================
# Priced Evidence
# ============================================================================

@dataclass(slots=True)
class PricedEvidence(TimeStampedEvidence):
    """
    Base class for evidence containing quantity and price information.
    """

    quantity: float = 0.0

    price: float = 0.0

    value: float = 0.0


# ============================================================================
# Terminal Evidence
# ============================================================================

@dataclass(slots=True)
class TerminalEvidence(InfrastructureEvidence):
    """
    Canonical desktop terminal information.

    Represents the desktop trading application currently connected to TTL.
    """

    terminal_id: Optional[str] = None

    terminal_name: str = ""

    platform_build: Optional[str] = None

    executable_path: Optional[str] = None

    installation_directory: Optional[str] = None

    operating_system: Optional[str] = None

    architecture: Optional[str] = None

    language: Optional[str] = None

    timezone: Optional[str] = None

    connection_status: ConnectionStatus = ConnectionStatus.UNKNOWN

    connected_at: Optional[datetime] = None

    disconnected_at: Optional[datetime] = None

    last_heartbeat: Optional[datetime] = None

    last_synchronization: Optional[datetime] = None

    session_id: Optional[str] = None

    session_active: bool = False


# ============================================================================
# User Evidence
# ============================================================================

@dataclass(slots=True)
class UserEvidence(InfrastructureEvidence):
    """
    Canonical authenticated trading user.

    Represents the operator currently authenticated
    within the desktop trading platform.
    """

    user_id: Optional[str] = None

    login: Optional[str] = None

    display_name: Optional[str] = None

    first_name: Optional[str] = None

    last_name: Optional[str] = None

    email: Optional[str] = None

    company: Optional[str] = None

    permissions: List[str] = field(default_factory=list)

    authentication_method: Optional[str] = None

    authenticated: bool = False

    login_time: Optional[datetime] = None

    last_activity: Optional[datetime] = None

    locale: Optional[str] = None


# ============================================================================
# Broker Evidence
# ============================================================================

@dataclass(slots=True)
class BrokerEvidence(InfrastructureEvidence):
    """
    Canonical broker identity.

    Describes the financial institution providing
    execution services.
    """

    broker_id: Optional[str] = None

    broker_name: str = ""

    legal_name: Optional[str] = None

    brand_name: Optional[str] = None

    broker_type: Optional[str] = None

    regulator: Optional[str] = None

    regulation_number: Optional[str] = None

    country: Optional[str] = None

    headquarters: Optional[str] = None

    website: Optional[str] = None

    support_email: Optional[str] = None

    support_phone: Optional[str] = None

    execution_model: Optional[str] = None

    liquidity_model: Optional[str] = None

    hedging_supported: Optional[bool] = None

    netting_supported: Optional[bool] = None


# ============================================================================
# Server Evidence
# ============================================================================

@dataclass(slots=True)
class ServerEvidence(InfrastructureEvidence):
    """
    Canonical trading server information.

    Represents the execution server connected by
    the desktop platform.
    """

    server_id: Optional[str] = None

    server_name: str = ""

    server_address: Optional[str] = None

    server_region: Optional[str] = None

    server_timezone: Optional[str] = None

    server_version: Optional[str] = None

    environment: Optional[str] = None

    connection_status: ConnectionStatus = ConnectionStatus.UNKNOWN

    ping_ms: Optional[float] = None

    latency_ms: Optional[float] = None

    heartbeat_interval_ms: Optional[int] = None

    last_heartbeat: Optional[datetime] = None

    connected_at: Optional[datetime] = None

    disconnected_at: Optional[datetime] = None

    maintenance_mode: bool = False


# ============================================================================
# Account Evidence
# ============================================================================

@dataclass(slots=True)
class AccountEvidence(InfrastructureEvidence):
    """
    Canonical trading account.

    Every supported desktop platform maps its native
    account representation into this institutional model.
    """

    broker_account_id: Optional[str] = None

    account_name: Optional[str] = None

    account_alias: Optional[str] = None

    account_type: Optional[str] = None

    currency: Optional[str] = None

    leverage: Optional[float] = None

    owner_name: Optional[str] = None

    owner_company: Optional[str] = None

    investor_mode: bool = False

    trading_enabled: bool = True

    read_only: bool = False

    hedging_enabled: Optional[bool] = None

    netting_enabled: Optional[bool] = None

    margin_mode: Optional[str] = None

    stop_out_mode: Optional[str] = None

    account_state: AccountState = AccountState.UNKNOWN

    created_at: Optional[datetime] = None

    last_login: Optional[datetime] = None

    broker_id: Optional[str] = None

    server_id: Optional[str] = None

    user_id: Optional[str] = None


# ============================================================================
# Balance Evidence
# ============================================================================

@dataclass(slots=True)
class BalanceEvidence(FinancialEvidence):
    """
    Canonical financial balance information.

    Represents the financial state of a trading account at the
    moment evidence was synchronized.
    """

    balance_id: Optional[str] = None

    balance: float = 0.0

    equity: float = 0.0

    credit: float = 0.0

    floating_profit: float = 0.0

    realized_profit: float = 0.0

    unrealized_profit: float = 0.0

    cash: float = 0.0

    available_funds: float = 0.0

    withdrawable_funds: Optional[float] = None

    buying_power: float = 0.0

    reserved_funds: float = 0.0

    bonus: float = 0.0

    account_value: Optional[float] = None


# ============================================================================
# Margin Evidence
# ============================================================================

@dataclass(slots=True)
class MarginEvidence(FinancialEvidence):
    """
    Canonical margin information.

    Represents the current margin state of the account.
    """

    margin_id: Optional[str] = None

    margin_used: float = 0.0

    free_margin: float = 0.0

    margin_level: float = 0.0

    initial_margin: float = 0.0

    maintenance_margin: float = 0.0

    required_margin: float = 0.0

    available_margin: float = 0.0

    stop_out_level: Optional[float] = None

    margin_call_level: Optional[float] = None

    leverage: Optional[float] = None

    risk_exposure: float = 0.0

    margin_utilization: Optional[float] = None


# ============================================================================
# Equity Evidence
# ============================================================================

@dataclass(slots=True)
class EquityEvidence(FinancialEvidence):
    """
    Canonical account equity information.

    Represents the mark-to-market valuation of the account.
    """

    equity_id: Optional[str] = None

    opening_balance: float = 0.0

    current_balance: float = 0.0

    current_equity: float = 0.0

    peak_equity: Optional[float] = None

    minimum_equity: Optional[float] = None

    floating_profit: float = 0.0

    realized_profit: float = 0.0

    unrealized_profit: float = 0.0

    daily_profit: float = 0.0

    weekly_profit: float = 0.0

    monthly_profit: float = 0.0

    account_return_pct: Optional[float] = None


# ============================================================================
# Buying Power Evidence
# ============================================================================

@dataclass(slots=True)
class BuyingPowerEvidence(FinancialEvidence):
    """
    Canonical buying power information.

    Represents the capital currently available
    for opening additional positions.
    """

    buying_power_id: Optional[str] = None

    buying_power: float = 0.0

    available_margin: float = 0.0

    available_equity: float = 0.0

    maximum_position_value: Optional[float] = None

    leverage: Optional[float] = None

    available_risk: Optional[float] = None


# ============================================================================
# Symbol Evidence
# ============================================================================

@dataclass(slots=True)
class SymbolEvidence(MarketEvidence):
    """
    Canonical financial instrument.

    Represents a tradable instrument independently of the trading
    platform or broker.
    """

    symbol_id: Optional[str] = None

    display_name: Optional[str] = None

    description: Optional[str] = None

    base_currency: Optional[str] = None

    quote_currency: Optional[str] = None

    contract_size: Optional[float] = None

    point_size: Optional[float] = None

    tick_size: Optional[float] = None

    tick_value: Optional[float] = None

    lot_size: Optional[float] = None

    minimum_volume: Optional[float] = None

    maximum_volume: Optional[float] = None

    volume_step: Optional[float] = None

    leverage: Optional[float] = None

    margin_currency: Optional[str] = None

    trading_enabled: bool = True

    short_selling_allowed: Optional[bool] = None

    expiration_date: Optional[datetime] = None


# ============================================================================
# Price Evidence
# ============================================================================

@dataclass(slots=True)
class PriceEvidence(MarketEvidence):
    """
    Canonical market price snapshot.
    """

    price_id: Optional[str] = None

    bid: Optional[float] = None

    ask: Optional[float] = None

    last: Optional[float] = None

    open: Optional[float] = None

    high: Optional[float] = None

    low: Optional[float] = None

    close: Optional[float] = None

    settlement: Optional[float] = None

    midpoint: Optional[float] = None

    spread: Optional[float] = None

    volume: Optional[float] = None

    open_interest: Optional[float] = None

    timestamp: Optional[datetime] = None

    market_status: Optional[str] = None

    trading_session: Optional[str] = None

    quote_source: Optional[str] = None


# ============================================================================
# Order Evidence
# ============================================================================

@dataclass(slots=True)
class OrderEvidence(PricedEvidence):
    """
    Canonical order submitted to a trading venue.
    """

    order_id: Optional[str] = None

    client_order_id: Optional[str] = None

    parent_order_id: Optional[str] = None

    order_type: Optional[str] = None

    side: Optional[str] = None

    status: Optional[str] = None

    time_in_force: Optional[str] = None

    stop_price: Optional[float] = None

    limit_price: Optional[float] = None

    filled_quantity: float = 0.0

    remaining_quantity: float = 0.0

    average_fill_price: Optional[float] = None

    commission: float = 0.0

    swap: float = 0.0

    comment: Optional[str] = None

    strategy_id: Optional[str] = None


# ============================================================================
# Execution Evidence
# ============================================================================

@dataclass(slots=True)
class ExecutionEvidence(PricedEvidence):
    """
    Canonical execution event generated by an order.
    """

    execution_id: Optional[str] = None

    order_id: Optional[str] = None

    execution_type: Optional[str] = None

    execution_price: float = 0.0

    execution_quantity: float = 0.0

    execution_value: float = 0.0

    execution_time: Optional[datetime] = None

    liquidity: Optional[str] = None

    venue: Optional[str] = None

    execution_reference: Optional[str] = None

    commission: float = 0.0

    fees: float = 0.0

    taxes: float = 0.0

    slippage: Optional[float] = None


# ============================================================================
# Deal Evidence
# ============================================================================

@dataclass(slots=True)
class DealEvidence(PricedEvidence):
    """
    Canonical broker fill.

    Some platforms expose fills separately from executions.
    """

    deal_id: Optional[str] = None

    execution_id: Optional[str] = None

    order_id: Optional[str] = None

    deal_type: Optional[str] = None

    side: Optional[str] = None

    realized_pnl: float = 0.0

    commission: float = 0.0

    swap: float = 0.0

    fee: float = 0.0

    deal_time: Optional[datetime] = None

    external_reference: Optional[str] = None


# ============================================================================
# Trade Evidence
# ============================================================================

@dataclass(slots=True)
class TradeEvidence(PricedEvidence):
    """
    Canonical completed trade.

    Represents the institutional trading record after one or more
    executions have been combined into a single trade.
    """

    trade_id: Optional[str] = None

    broker_trade_id: Optional[str] = None

    order_id: Optional[str] = None

    execution_id: Optional[str] = None

    deal_id: Optional[str] = None

    parent_trade_id: Optional[str] = None

    side: Optional[str] = None

    trade_status: Optional[str] = None

    entry_price: Optional[float] = None

    exit_price: Optional[float] = None

    average_entry_price: Optional[float] = None

    average_exit_price: Optional[float] = None

    stop_loss: Optional[float] = None

    take_profit: Optional[float] = None

    realized_pnl: float = 0.0

    unrealized_pnl: float = 0.0

    gross_pnl: float = 0.0

    net_pnl: float = 0.0

    commission: float = 0.0

    swap: float = 0.0

    fees: float = 0.0

    slippage: float = 0.0

    strategy_id: Optional[str] = None

    strategy_name: Optional[str] = None

    broker_ticket: Optional[str] = None

    trade_reference: Optional[str] = None


# ============================================================================
# Position Evidence
# ============================================================================

@dataclass(slots=True)
class PositionEvidence(PricedEvidence):
    """
    Canonical open trading position.

    Represents the current market exposure of an account.
    """

    position_id: Optional[str] = None

    broker_position_id: Optional[str] = None

    trade_id: Optional[str] = None

    side: Optional[str] = None

    position_status: Optional[str] = None

    open_price: float = 0.0

    current_price: float = 0.0

    average_price: Optional[float] = None

    stop_loss: Optional[float] = None

    take_profit: Optional[float] = None

    unrealized_pnl: float = 0.0

    realized_pnl: float = 0.0

    gross_pnl: float = 0.0

    net_pnl: float = 0.0

    margin_used: float = 0.0

    exposure: float = 0.0

    overnight_swap: float = 0.0

    liquidation_price: Optional[float] = None

    risk_percentage: Optional[float] = None

    account_exposure_pct: Optional[float] = None

    floating_drawdown: Optional[float] = None

    highest_profit: Optional[float] = None

    maximum_drawdown: Optional[float] = None

    hedge_group: Optional[str] = None


# ============================================================================
# History Evidence
# ============================================================================

@dataclass(slots=True)
class HistoryEvidence(MarketEvidence):
    """
    Canonical historical trading archive.

    Represents a synchronized snapshot of historical trading
    activity for an account.
    """

    history_id: Optional[str] = None

    from_time: Optional[datetime] = None

    to_time: Optional[datetime] = None

    synchronized_at: Optional[datetime] = None

    history_source: Optional[str] = None

    history_status: Optional[str] = None

    orders: List[str] = field(default_factory=list)

    executions: List[str] = field(default_factory=list)

    deals: List[str] = field(default_factory=list)

    trades: List[str] = field(default_factory=list)

    positions: List[str] = field(default_factory=list)

    total_orders: int = 0

    total_executions: int = 0

    total_deals: int = 0

    total_trades: int = 0

    total_positions: int = 0

    summary: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Activity Evidence
# ============================================================================

@dataclass(slots=True)
class ActivityEvidence(MarketEvidence):
    """
    Canonical activity event.

    Represents operational activity occurring inside a
    desktop trading platform.
    """

    activity_id: Optional[str] = None

    activity_type: Optional[str] = None

    category: Optional[str] = None

    severity: Optional[str] = None

    message: Optional[str] = None

    source: Optional[str] = None

    reference_id: Optional[str] = None

    user_id: Optional[str] = None

    terminal_id: Optional[str] = None

    broker_id: Optional[str] = None

    server_id: Optional[str] = None

    occurred_at: Optional[datetime] = None

    acknowledged: bool = False

    details: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Desktop Evidence Package
# ============================================================================

@dataclass(slots=True)
class DesktopEvidencePackage:
    """
    Canonical synchronization package produced by every desktop connector.

    Every synchronization cycle produces exactly one evidence package.
    """

    terminal: Optional[TerminalEvidence] = None

    user: Optional[UserEvidence] = None

    broker: Optional[BrokerEvidence] = None

    server: Optional[ServerEvidence] = None

    account: Optional[AccountEvidence] = None

    balance: Optional[BalanceEvidence] = None

    margin: Optional[MarginEvidence] = None

    equity: Optional[EquityEvidence] = None

    buying_power: Optional[BuyingPowerEvidence] = None

    symbols: List[SymbolEvidence] = field(default_factory=list)

    prices: List[PriceEvidence] = field(default_factory=list)

    orders: List[OrderEvidence] = field(default_factory=list)

    executions: List[ExecutionEvidence] = field(default_factory=list)

    deals: List[DealEvidence] = field(default_factory=list)

    trades: List[TradeEvidence] = field(default_factory=list)

    positions: List[PositionEvidence] = field(default_factory=list)

    history: Optional[HistoryEvidence] = None

    activities: List[ActivityEvidence] = field(default_factory=list)

    synchronized_at: datetime = field(default_factory=datetime.utcnow)

    synchronization_id: str = field(default_factory=lambda: str(uuid4()))

    connector_name: Optional[str] = None

    connector_version: Optional[str] = None

    schema_version: str = EVIDENCE_SCHEMA_VERSION


# ============================================================================
# Validation Helpers
# ============================================================================

def validate_evidence(evidence: Evidence) -> bool:
    """
    Basic structural validation for canonical evidence.
    """

    if evidence is None:
        return False

    if evidence.identity is None:
        return False

    if evidence.metadata is None:
        return False

    if evidence.provenance is None:
        return False

    return True


def validate_package(package: DesktopEvidencePackage) -> bool:
    """
    Validate an evidence package before it enters TTL.
    """

    if package is None:
        return False

    for evidence in (
        package.terminal,
        package.user,
        package.broker,
        package.server,
        package.account,
        package.balance,
        package.margin,
        package.equity,
        package.buying_power,
        package.history,
    ):
        if evidence is not None and not validate_evidence(evidence):
            return False

    collections = (
        package.symbols,
        package.prices,
        package.orders,
        package.executions,
        package.deals,
        package.trades,
        package.positions,
        package.activities,
    )

    for collection in collections:
        for item in collection:
            if not validate_evidence(item):
                return False

    return True


# ============================================================================
# Factory Helpers
# ============================================================================

def create_empty_package() -> DesktopEvidencePackage:
    """
    Create an empty institutional evidence package.
    """

    return DesktopEvidencePackage()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    # Identity
    "EvidenceIdentity",
    "EvidenceMetadata",
    "EvidenceProvenance",

    # Base
    "Evidence",
    "InfrastructureEvidence",
    "FinancialEvidence",
    "MarketEvidence",
    "TimeStampedEvidence",
    "PricedEvidence",

    # Infrastructure
    "TerminalEvidence",
    "UserEvidence",
    "BrokerEvidence",
    "ServerEvidence",
    "AccountEvidence",

    # Financial
    "BalanceEvidence",
    "MarginEvidence",
    "EquityEvidence",
    "BuyingPowerEvidence",

    # Market
    "SymbolEvidence",
    "PriceEvidence",
    "OrderEvidence",
    "ExecutionEvidence",
    "DealEvidence",
    "TradeEvidence",
    "PositionEvidence",
    "HistoryEvidence",
    "ActivityEvidence",

    # Package
    "DesktopEvidencePackage",

    # Helpers
    "validate_evidence",
    "validate_package",
    "create_empty_package",
]