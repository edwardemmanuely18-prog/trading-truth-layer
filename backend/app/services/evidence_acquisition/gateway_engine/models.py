"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Gateway Engine

Canonical Evidence Models

This module defines the institutional evidence contracts used by every
gateway provider supported by TTL.

Providers include (but are not limited to):

- FIX
- Interactive Brokers Gateway
- Trader Workstation (TWS)
- REST APIs
- WebSocket APIs
- gRPC Services
- OpenAPI Services

No provider-specific objects should exist inside this module.

Every gateway provider must translate its native protocol objects into
these canonical evidence models before evidence is consumed elsewhere
inside Trading Truth Layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import uuid4


# ============================================================================
# Evidence Schema
# ============================================================================

EVIDENCE_SCHEMA_VERSION = "1.0"


# ============================================================================
# Provider Type
# ============================================================================


class ProviderType(str, Enum):
    """
    Evidence provider category.
    """

    GATEWAY = "gateway"


# ============================================================================
# Gateway Types
# ============================================================================


class GatewayType(str, Enum):
    """
    Canonical gateway technologies.
    """

    FIX = "fix"

    IBKR_GATEWAY = "ibkr_gateway"

    IBKR_CLIENT_PORTAL = "ibkr_client_portal"

    MT5 = "mt5"

    CTRADER = "ctrader"

    NINJATRADER = "ninjatrader"

    TRADESTATION = "tradestation"

    BINANCE = "binance"

    BYBIT = "bybit"

    KRAKEN = "kraken"

    TWS = "tws"

    REST = "rest"

    WEBSOCKET = "websocket"

    GRPC = "grpc"

    OPENAPI = "openapi"

    UNKNOWN = "unknown"


# ============================================================================
# Connection Status
# ============================================================================


class ConnectionStatus(str, Enum):
    """
    Gateway connection status.
    """

    CONNECTED = "connected"

    CONNECTING = "connecting"

    DISCONNECTED = "disconnected"

    RECONNECTING = "reconnecting"

    FAILED = "failed"

    UNKNOWN = "unknown"


# ============================================================================
# Session Status
# ============================================================================


class SessionStatus(str, Enum):
    """
    Gateway session lifecycle.
    """

    CREATED = "created"

    AUTHENTICATING = "authenticating"

    ACTIVE = "active"

    EXPIRED = "expired"

    CLOSED = "closed"

    FAILED = "failed"

    UNKNOWN = "unknown"


# ============================================================================
# Synchronization Status
# ============================================================================


class SynchronizationStatus(str, Enum):
    """
    Synchronization lifecycle.
    """

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    PARTIAL = "partial"


# ============================================================================
# Evidence Source
# ============================================================================


class EvidenceSource(str, Enum):
    """
    How gateway evidence was acquired.
    """

    API = "api"

    FIX = "fix"

    WEBSOCKET = "websocket"

    GRPC = "grpc"

    REST = "rest"

    OPENAPI = "openapi"

    SDK = "sdk"

    MANUAL = "manual"

    UNKNOWN = "unknown"


# ============================================================================
# Provenance Level
# ============================================================================


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


# ============================================================================
# Identity
# ============================================================================


@dataclass(slots=True)
class EvidenceIdentity:
    """
    Canonical identity shared by every gateway evidence object.
    """

    evidence_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    workspace_id: Optional[int] = None

    provider_name: str = ""

    provider_type: ProviderType = (
        ProviderType.GATEWAY
    )

    gateway_type: GatewayType = (
        GatewayType.UNKNOWN
    )

    gateway_version: Optional[str] = None

    endpoint: Optional[str] = None

    session_id: Optional[str] = None

    account_id: Optional[str] = None

    organization_id: Optional[str] = None

    workspace_slug: Optional[str] = None

    provider_account_key: Optional[str] = None


# ============================================================================
# Metadata
# ============================================================================


@dataclass(slots=True)
class EvidenceMetadata:
    """
    Operational synchronization metadata.
    """

    synchronization_id: Optional[str] = None

    synchronization_status: SynchronizationStatus = (
        SynchronizationStatus.PENDING
    )

    synchronized_at: Optional[datetime] = None

    captured_at: datetime = field(
        default_factory=datetime.utcnow
    )

    evidence_version: str = (
        EVIDENCE_SCHEMA_VERSION
    )

    source: EvidenceSource = (
        EvidenceSource.UNKNOWN
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# Provenance
# ============================================================================


@dataclass(slots=True)
class EvidenceProvenance:
    """
    Institutional evidence provenance.
    """

    provenance_level: ProvenanceLevel = (
        ProvenanceLevel.UNKNOWN
    )

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
    Root gateway evidence object.
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
    Base infrastructure evidence.
    """

    active: bool = True


# ============================================================================
# Financial Evidence
# ============================================================================


@dataclass(slots=True)
class FinancialEvidence(Evidence):
    """
    Base financial snapshot evidence.
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
    Base market evidence.
    """

    account_id: Optional[str] = None

    symbol: Optional[str] = None

    exchange: Optional[str] = None

    asset_class: Optional[str] = None

    market: Optional[str] = None


# ============================================================================
# Timestamped Evidence
# ============================================================================


@dataclass(slots=True)
class TimeStampedEvidence(MarketEvidence):
    """
    Market evidence with lifecycle timestamps.
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
    Base priced market evidence.
    """

    quantity: float = 0.0

    price: float = 0.0

    value: float = 0.0


# ============================================================================
# Gateway Evidence
# ============================================================================


@dataclass(slots=True)
class GatewayEvidence(InfrastructureEvidence):
    """
    Canonical gateway instance.

    Represents the gateway software or service connected to TTL.
    """

    gateway_id: Optional[str] = None

    gateway_name: str = ""

    gateway_type: GatewayType = GatewayType.UNKNOWN

    gateway_version: Optional[str] = None

    implementation: Optional[str] = None

    vendor: Optional[str] = None

    executable_path: Optional[str] = None

    host: Optional[str] = None

    port: Optional[int] = None

    secure_connection: bool = False

    connection_status: ConnectionStatus = (
        ConnectionStatus.UNKNOWN
    )

    connected_at: Optional[datetime] = None

    disconnected_at: Optional[datetime] = None

    last_heartbeat: Optional[datetime] = None

    protocol: Optional[str] = None

    transport: Optional[str] = None


# ============================================================================
# Session Evidence
# ============================================================================


@dataclass(slots=True)
class SessionEvidence(InfrastructureEvidence):
    """
    Canonical gateway session.
    """

    session_id: Optional[str] = None

    session_status: SessionStatus = (
        SessionStatus.UNKNOWN
    )

    login_time: Optional[datetime] = None

    logout_time: Optional[datetime] = None

    expiration_time: Optional[datetime] = None

    authenticated: bool = False

    heartbeat_interval_seconds: Optional[int] = None

    last_heartbeat: Optional[datetime] = None

    remote_address: Optional[str] = None

    local_address: Optional[str] = None

    reconnect_count: int = 0


# ============================================================================
# Authentication Evidence
# ============================================================================


@dataclass(slots=True)
class AuthenticationEvidence(InfrastructureEvidence):
    """
    Authentication information associated with the gateway.
    """

    authentication_id: Optional[str] = None

    authentication_method: Optional[str] = None

    authenticated: bool = False

    username: Optional[str] = None

    account_id: Optional[str] = None

    organization: Optional[str] = None

    api_key_present: bool = False

    certificate_present: bool = False

    token_present: bool = False

    token_expiration: Optional[datetime] = None

    permissions: List[str] = field(
        default_factory=list
    )


# ============================================================================
# Endpoint Evidence
# ============================================================================


@dataclass(slots=True)
class EndpointEvidence(InfrastructureEvidence):
    """
    Canonical communication endpoint.
    """

    endpoint_id: Optional[str] = None

    endpoint_name: Optional[str] = None

    endpoint_url: Optional[str] = None

    host: Optional[str] = None

    port: Optional[int] = None

    protocol: Optional[str] = None

    transport: Optional[str] = None

    secure: bool = False

    available: bool = False

    latency_ms: Optional[float] = None

    timeout_seconds: Optional[int] = None

    rate_limit: Optional[int] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# Connection Evidence
# ============================================================================


@dataclass(slots=True)
class ConnectionEvidence(InfrastructureEvidence):
    """
    Canonical network connection state.
    """

    connection_id: Optional[str] = None

    provider_connection_id: Optional[str] = None

    connection_status: ConnectionStatus = (
        ConnectionStatus.UNKNOWN
    )

    established_at: Optional[datetime] = None

    closed_at: Optional[datetime] = None

    remote_ip: Optional[str] = None

    remote_port: Optional[int] = None

    local_ip: Optional[str] = None

    local_port: Optional[int] = None

    bytes_sent: int = 0

    bytes_received: int = 0

    reconnect_attempts: int = 0

    encrypted: bool = False

    compression_enabled: bool = False


# ============================================================================
# Gateway Account Evidence
# ============================================================================


@dataclass(slots=True)
class AccountEvidence(InfrastructureEvidence):
    """
    Canonical account accessible through a gateway.

    This is intentionally gateway-neutral and represents the
    account identity exposed by the communication layer rather
    than a trading account snapshot.
    """

    gateway_account_id: Optional[str] = None

    account_id: Optional[str] = None

    account_name: Optional[str] = None

    account_alias: Optional[str] = None

    organization_id: Optional[str] = None

    organization_name: Optional[str] = None

    broker_name: Optional[str] = None

    environment: Optional[str] = None

    currency: Optional[str] = None

    timezone: Optional[str] = None

    active: bool = True

    read_only: bool = False

    permissions: List[str] = field(
        default_factory=list
    )


# ============================================================================
# Instrument Evidence
# ============================================================================


@dataclass(slots=True)
class InstrumentEvidence(MarketEvidence):
    """
    Canonical financial instrument available through the gateway.
    """

    instrument_id: Optional[str] = None

    security_id: Optional[str] = None

    security_type: Optional[str] = None

    symbol_description: Optional[str] = None

    base_currency: Optional[str] = None

    quote_currency: Optional[str] = None

    contract_size: Optional[float] = None

    tick_size: Optional[float] = None

    tick_value: Optional[float] = None

    minimum_quantity: Optional[float] = None

    maximum_quantity: Optional[float] = None

    quantity_increment: Optional[float] = None

    trading_enabled: bool = True


# ============================================================================
# Market Data Evidence
# ============================================================================


@dataclass(slots=True)
class MarketDataEvidence(MarketEvidence):
    """
    Canonical market data snapshot.
    """

    market_data_id: Optional[str] = None

    bid: Optional[float] = None

    ask: Optional[float] = None

    last: Optional[float] = None

    open_price: Optional[float] = None

    high_price: Optional[float] = None

    low_price: Optional[float] = None

    close_price: Optional[float] = None

    volume: Optional[float] = None

    open_interest: Optional[float] = None

    market_timestamp: Optional[datetime] = None


# ============================================================================
# Quote Evidence
# ============================================================================


@dataclass(slots=True)
class QuoteEvidence(MarketEvidence):
    """
    Canonical executable quote.
    """

    quote_id: Optional[str] = None

    bid_price: Optional[float] = None

    ask_price: Optional[float] = None

    bid_size: Optional[float] = None

    ask_size: Optional[float] = None

    spread: Optional[float] = None

    quote_timestamp: Optional[datetime] = None

    executable: bool = True


# ============================================================================
# Order Evidence
# ============================================================================


@dataclass(slots=True)
class OrderEvidence(PricedEvidence):
    """
    Canonical order transmitted through a gateway.
    """

    order_id: Optional[str] = None

    client_order_id: Optional[str] = None

    parent_order_id: Optional[str] = None

    broker_order_id: Optional[str] = None

    order_type: Optional[str] = None

    side: Optional[str] = None

    status: Optional[str] = None

    filled_quantity: float = 0.0

    remaining_quantity: float = 0.0

    average_fill_price: Optional[float] = None

    stop_price: Optional[float] = None

    limit_price: Optional[float] = None

    time_in_force: Optional[str] = None

    routing_destination: Optional[str] = None

    strategy_name: Optional[str] = None


# ============================================================================
# Execution Evidence
# ============================================================================


@dataclass(slots=True)
class ExecutionEvidence(PricedEvidence):
    """
    Canonical execution report.
    """

    execution_id: Optional[str] = None

    execution_type: Optional[str] = None

    execution_status: Optional[str] = None

    execution_time: Optional[datetime] = None

    order_id: Optional[str] = None

    client_order_id: Optional[str] = None

    broker_execution_id: Optional[str] = None

    liquidity_flag: Optional[str] = None

    commission: Optional[float] = None

    fees: Optional[float] = None

    exchange: Optional[str] = None

    venue: Optional[str] = None


# ============================================================================
# Position Evidence
# ============================================================================


@dataclass(slots=True)
class PositionEvidence(PricedEvidence):
    """
    Canonical open position.
    """

    position_id: Optional[str] = None

    direction: Optional[str] = None

    average_price: Optional[float] = None

    current_price: Optional[float] = None

    market_value: Optional[float] = None

    unrealized_pnl: Optional[float] = None

    realized_pnl: Optional[float] = None

    swap: Optional[float] = None

    commission: Optional[float] = None

    margin_used: Optional[float] = None


# ============================================================================
# Trade Evidence
# ============================================================================


@dataclass(slots=True)
class TradeEvidence(PricedEvidence):
    """
    Canonical completed trade.
    """

    trade_id: Optional[str] = None

    order_id: Optional[str] = None

    execution_id: Optional[str] = None

    position_id: Optional[str] = None

    side: Optional[str] = None

    trade_time: Optional[datetime] = None

    gross_pnl: Optional[float] = None

    net_pnl: Optional[float] = None

    commission: Optional[float] = None

    fees: Optional[float] = None

    swap: Optional[float] = None

    realized: bool = False


# ============================================================================
# Synchronization Statistics
# ============================================================================


@dataclass(slots=True)
class SynchronizationStatistics:
    """
    Statistics describing a gateway synchronization cycle.
    """

    evidence_objects: int = 0

    infrastructure_objects: int = 0

    market_objects: int = 0

    financial_objects: int = 0

    translated_objects: int = 0

    validation_errors: int = 0

    translation_errors: int = 0

    warnings: int = 0


# ============================================================================
# Synchronization Summary
# ============================================================================


@dataclass(slots=True)
class SynchronizationSummary:
    """
    Human-readable synchronization summary.
    """

    synchronization_id: Optional[str] = None

    provider_name: Optional[str] = None

    provider_version: Optional[str] = None

    gateway_type: GatewayType = (
        GatewayType.UNKNOWN
    )

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    successful: bool = False

    message: Optional[str] = None

    statistics: SynchronizationStatistics = field(
        default_factory=SynchronizationStatistics
    )


# ============================================================================
# Gateway Evidence Package
# ============================================================================


@dataclass(slots=True)
class GatewayEvidencePackage:
    """
    Canonical evidence package produced by every Gateway Engine provider.

    This is the only object consumed by higher layers of TTL.
    """

    summary: SynchronizationSummary = field(
        default_factory=SynchronizationSummary
    )

    gateway: Optional[GatewayEvidence] = None

    session: Optional[SessionEvidence] = None

    authentication: Optional[AuthenticationEvidence] = None

    endpoint: Optional[EndpointEvidence] = None

    connection: Optional[ConnectionEvidence] = None

    account: Optional[AccountEvidence] = None

    instruments: List[InstrumentEvidence] = field(
        default_factory=list
    )

    market_data: List[MarketDataEvidence] = field(
        default_factory=list
    )

    quotes: List[QuoteEvidence] = field(
        default_factory=list
    )

    orders: List[OrderEvidence] = field(
        default_factory=list
    )

    executions: List[ExecutionEvidence] = field(
        default_factory=list
    )

    positions: List[PositionEvidence] = field(
        default_factory=list
    )

    trades: List[TradeEvidence] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# Convenience Properties
# ============================================================================


    @property
    def provider_name(self) -> Optional[str]:
        return self.summary.provider_name

    @property
    def provider_version(self) -> Optional[str]:
        return self.summary.provider_version

    @property
    def successful(self) -> bool:
        return self.summary.successful

    @property
    def synchronization_id(self) -> Optional[str]:
        return self.summary.synchronization_id

    @property
    def evidence_count(self) -> int:
        """
        Total canonical evidence objects contained
        within this package.
        """

        total = 0

        singleton_objects = [
            self.gateway,
            self.session,
            self.authentication,
            self.endpoint,
            self.connection,
            self.account,
        ]

        total += sum(
            1 for item in singleton_objects
            if item is not None
        )

        total += len(self.instruments)

        total += len(self.market_data)

        total += len(self.quotes)

        total += len(self.orders)

        total += len(self.executions)

        total += len(self.positions)

        total += len(self.trades)

        return total


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    # Constants
    "EVIDENCE_SCHEMA_VERSION",

    # Enumerations
    "ProviderType",
    "GatewayType",
    "ConnectionStatus",
    "SessionStatus",
    "SynchronizationStatus",
    "EvidenceSource",
    "ProvenanceLevel",

    # Core Models
    "EvidenceIdentity",
    "EvidenceMetadata",
    "EvidenceProvenance",
    "Evidence",
    "InfrastructureEvidence",
    "FinancialEvidence",
    "MarketEvidence",
    "TimeStampedEvidence",
    "PricedEvidence",

    # Infrastructure Evidence
    "GatewayEvidence",
    "SessionEvidence",
    "AuthenticationEvidence",
    "EndpointEvidence",
    "ConnectionEvidence",
    "AccountEvidence",

    # Market Evidence
    "InstrumentEvidence",
    "MarketDataEvidence",
    "QuoteEvidence",
    "OrderEvidence",
    "ExecutionEvidence",
    "PositionEvidence",
    "TradeEvidence",

    # Synchronization
    "SynchronizationStatistics",
    "SynchronizationSummary",

    # Package
    "GatewayEvidencePackage",
]