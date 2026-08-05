from __future__ import annotations

"""
Institutional Raw Evidence

RawEvidence is the broker-neutral transport object exchanged between the
Desktop Trading Engine and the Universal Evidence Adapter (UEA).

Every supported broker MUST emit RawEvidence before entering the UEA.

Responsibilities
----------------

• Represent one standardized broker evidence object
• Preserve original provider identifiers
• Preserve trading information
• Preserve financial information
• Preserve raw provider payload
• Carry synchronization metadata

RawEvidence is NOT canonical evidence.

CanonicalEvidence is produced later by the EvidenceCanonicalizer.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .raw_metadata import RawMetadata


# ============================================================================
# Evidence Types
# ============================================================================

class EvidenceType(str, Enum):

    TRADE = "TRADE"

    ORDER = "ORDER"

    POSITION = "POSITION"

    EXECUTION = "EXECUTION"

    DEAL = "DEAL"

    ACCOUNT = "ACCOUNT"

    BALANCE = "BALANCE"

    EQUITY = "EQUITY"

    MARGIN = "MARGIN"

    DEPOSIT = "DEPOSIT"

    WITHDRAWAL = "WITHDRAWAL"

    SYMBOL = "SYMBOL"

    HISTORY = "HISTORY"

    CUSTOM = "CUSTOM"


# ============================================================================
# Evidence Status
# ============================================================================

class EvidenceStatus(str, Enum):

    NEW = "NEW"

    UPDATED = "UPDATED"

    CLOSED = "CLOSED"

    CANCELLED = "CANCELLED"

    DELETED = "DELETED"

    UNKNOWN = "UNKNOWN"


# ============================================================================
# Original Provider Identifiers
# ============================================================================

@dataclass(slots=True)
class ProviderIdentifiers:
    """
    Original identifiers supplied by the broker.

    Every broker may populate only the identifiers that
    are applicable.
    """

    ticket_id: str | None = None

    order_id: str | None = None

    deal_id: str | None = None

    position_id: str | None = None

    execution_id: str | None = None

    trade_id: str | None = None

    external_id: str | None = None


# ============================================================================
# Instrument Information
# ============================================================================

@dataclass(slots=True)
class InstrumentInformation:

    symbol: str | None = None

    asset_class: str | None = None

    exchange: str | None = None

    market: str | None = None

    contract_size: float | None = None

    point_size: float | None = None


# ============================================================================
# Trading Information
# ============================================================================

@dataclass(slots=True)
class TradingInformation:

    side: str | None = None

    volume: float | None = None

    entry_price: float | None = None

    exit_price: float | None = None

    stop_loss: float | None = None

    take_profit: float | None = None

    commission: float | None = None

    swap: float | None = None

    fees: float | None = None

    profit: float | None = None

    balance: float | None = None

    equity: float | None = None

    margin: float | None = None

    free_margin: float | None = None

    margin_level: float | None = None


# ============================================================================
# Evidence Timing
# ============================================================================

@dataclass(slots=True)
class EvidenceTiming:

    created_at: datetime | None = None

    opened_at: datetime | None = None

    executed_at: datetime | None = None

    modified_at: datetime | None = None

    closed_at: datetime | None = None

    synchronized_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================================
# Raw Evidence
# ============================================================================

@dataclass(slots=True)
class RawEvidence:
    """
    Broker-neutral evidence transported from the Desktop
    Trading Engine to the Universal Evidence Adapter.
    """

    evidence_type: EvidenceType

    metadata: RawMetadata

    status: EvidenceStatus = EvidenceStatus.NEW

    provider_ids: ProviderIdentifiers = field(
        default_factory=ProviderIdentifiers
    )

    instrument: InstrumentInformation = field(
        default_factory=InstrumentInformation
    )

    trading: TradingInformation = field(
        default_factory=TradingInformation
    )

    timing: EvidenceTiming = field(
        default_factory=EvidenceTiming
    )

    raw_payload: dict[str, Any] = field(
        default_factory=dict
    )

    custom_fields: dict[str, Any] = field(
        default_factory=dict
    )

    tags: list[str] = field(
        default_factory=list
    )

    def validate(self) -> list[str]:
        """
        Validate transport integrity.
        """

        issues: list[str] = []

        issues.extend(self.metadata.validate())

        if self.evidence_type is None:
            issues.append("Evidence type is required.")

        if not isinstance(self.raw_payload, dict):
            issues.append("Raw payload must be a dictionary.")

        return issues

    @property
    def provider_name(self) -> str:
        return self.metadata.provider.provider_name

    @property
    def provider_platform(self) -> str:
        return self.metadata.provider.provider_platform

    @property
    def broker_account_id(self) -> str:
        return self.metadata.account.broker_account_id

    @property
    def account_state(self) -> str:
        return self.metadata.account.account_state

    @property
    def evidence_hash(self) -> str | None:
        return self.metadata.transport.evidence_hash

    @property
    def synchronization_id(self) -> str:
        return self.metadata.synchronization.synchronization_id

    def to_dict(self) -> dict[str, Any]:
        """
        Export the transport object for diagnostics,
        persistence or auditing.
        """

        return {
            "evidence_type": self.evidence_type.value,
            "status": self.status.value,
            "provider_name": self.provider_name,
            "provider_platform": self.provider_platform,
            "broker_account_id": self.broker_account_id,
            "account_state": self.account_state,
            "evidence_hash": self.evidence_hash,
            "synchronization_id": self.synchronization_id,
            "provider_identifiers": vars(self.provider_ids),
            "instrument": vars(self.instrument),
            "trading": vars(self.trading),
            "timing": {
                "created_at": self.timing.created_at,
                "opened_at": self.timing.opened_at,
                "executed_at": self.timing.executed_at,
                "modified_at": self.timing.modified_at,
                "closed_at": self.timing.closed_at,
                "synchronized_at": self.timing.synchronized_at,
            },
            "metadata": self.metadata.to_dict(),
            "tags": self.tags,
            "custom_fields": self.custom_fields,
            "raw_payload": self.raw_payload,
        }