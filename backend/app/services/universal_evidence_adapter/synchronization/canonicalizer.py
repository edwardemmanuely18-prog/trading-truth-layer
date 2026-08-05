from __future__ import annotations

"""
Institutional Evidence Canonicalizer

Transforms standardized broker evidence into the canonical evidence model
used throughout the Trading Truth Layer (TTL).

Responsibilities
----------------
- Produce broker-neutral canonical evidence
- Preserve provider identity
- Preserve synchronization identity
- Preserve execution information
- Preserve financial information
- Produce immutable canonical objects

The canonicalizer does NOT:
- Verify evidence
- Publish evidence
- Deduplicate evidence
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.services.universal_evidence_adapter.domain.transport.raw_evidence import (
    EvidenceType,
    RawEvidence,
)

from app.services.universal_evidence_adapter.synchronization.provenance_builder import (
    ProvenanceRecord,
)


# ============================================================================
# Canonical Identity
# ============================================================================

@dataclass(slots=True)
class CanonicalIdentity:

    canonical_evidence_id: str

    evidence_hash: str

    evidence_version: int = 1


# ============================================================================
# Provider Information
# ============================================================================

@dataclass(slots=True)
class ProviderInformation:

    provider_name: str

    provider_platform: str

    broker_server: str | None = None

    broker_account_id: str | None = None

    broker_account_name: str | None = None

    account_state: str | None = None

    account_currency: str | None = None


# ============================================================================
# Instrument Information
# ============================================================================

@dataclass(slots=True)
class InstrumentInformation:

    symbol: str | None = None

    asset_class: str | None = None

    market: str | None = None

    exchange: str | None = None


# ============================================================================
# Execution Information
# ============================================================================

@dataclass(slots=True)
class ExecutionInformation:

    ticket_id: str | None = None

    order_id: str | None = None

    deal_id: str | None = None

    position_id: str | None = None

    execution_id: str | None = None

    side: str | None = None

    volume: float | None = None

    entry_price: float | None = None

    exit_price: float | None = None

    executed_at: datetime | None = None


# ============================================================================
# Financial Information
# ============================================================================

@dataclass(slots=True)
class FinancialInformation:

    profit: float | None = None

    commission: float | None = None

    swap: float | None = None

    fees: float | None = None

    balance: float | None = None

    equity: float | None = None


# ============================================================================
# Canonical Evidence
# ============================================================================

@dataclass(slots=True)
class CanonicalEvidence:

    identity: CanonicalIdentity

    provider: ProviderInformation

    instrument: InstrumentInformation = field(
        default_factory=InstrumentInformation
    )

    execution: ExecutionInformation = field(
        default_factory=ExecutionInformation
    )

    financial: FinancialInformation = field(
        default_factory=FinancialInformation
    )

    provenance: ProvenanceRecord | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    synchronized_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    evidence_type: EvidenceType


# ============================================================================
# Evidence Canonicalizer
# ============================================================================

class EvidenceCanonicalizer:
    """
    Produces canonical evidence objects.
    """

    def canonicalize(
        self,
        *,
        identity: CanonicalIdentity,
        provider: ProviderInformation,
        evidence_type: EvidenceType,
        instrument: InstrumentInformation | None = None,
        execution: ExecutionInformation | None = None,
        financial: FinancialInformation | None = None,
        provenance: ProvenanceRecord | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CanonicalEvidence:

        return CanonicalEvidence(
            identity=identity,
            provider=provider,
            instrument=instrument or InstrumentInformation(),
            execution=execution or ExecutionInformation(),
            financial=financial or FinancialInformation(),
            provenance=provenance,
            metadata=metadata or {},
            evidence_type=evidence_type,
        )

    def canonicalize_raw(
        self,
        evidence: RawEvidence,
        *,
        canonical_evidence_id: str,
        provenance: ProvenanceRecord,
    ) -> CanonicalEvidence:
        """
        Transform RawEvidence into CanonicalEvidence.
        """

        return self.canonicalize(
            identity=CanonicalIdentity(
                canonical_evidence_id=canonical_evidence_id,
                evidence_hash=evidence.evidence_hash or "",
            ),
            provider=ProviderInformation(
                provider_name=evidence.provider_name,
                provider_platform=evidence.provider_platform,
                broker_server=evidence.metadata.provider.broker_server,
                broker_account_id=evidence.broker_account_id,
                broker_account_name=evidence.metadata.account.broker_account_name,
                account_state=evidence.account_state,
                account_currency=evidence.metadata.account.account_currency,
            ),
            evidence_type=evidence.evidence_type,
            instrument=InstrumentInformation(
                symbol=evidence.instrument.symbol,
                asset_class=evidence.instrument.asset_class,
                exchange=evidence.instrument.exchange,
                market=evidence.instrument.market,
            ),
            execution=ExecutionInformation(
                ticket_id=evidence.provider_ids.ticket_id,
                order_id=evidence.provider_ids.order_id,
                deal_id=evidence.provider_ids.deal_id,
                position_id=evidence.provider_ids.position_id,
                execution_id=evidence.provider_ids.execution_id,
                side=evidence.trading.side,
                volume=evidence.trading.volume,
                entry_price=evidence.trading.entry_price,
                exit_price=evidence.trading.exit_price,
                executed_at=evidence.timing.executed_at,
            ),
            financial=FinancialInformation(
                profit=evidence.trading.profit,
                commission=evidence.trading.commission,
                swap=evidence.trading.swap,
                fees=evidence.trading.fees,
                balance=evidence.trading.balance,
                equity=evidence.trading.equity,
            ),
            provenance=provenance,
            metadata=evidence.custom_fields,
        )

    def validate(
        self,
        evidence: CanonicalEvidence,
    ) -> list[str]:

        issues: list[str] = []

        if not evidence.identity.canonical_evidence_id:
            issues.append("Canonical evidence ID is required.")

        if not evidence.identity.evidence_hash:
            issues.append("Evidence hash is required.")

        if not evidence.provider.provider_name:
            issues.append("Provider name is required.")

        if not evidence.provider.provider_platform:
            issues.append("Provider platform is required.")

        return issues

    # ----------------------------------------------------------------------

    def process(
        self,
        *,
        evidence: RawEvidence,
        canonical_evidence_id: str,
        provenance: ProvenanceRecord,
    ) -> CanonicalEvidence:
        """
        Pipeline entry point.

        Produce canonical evidence.
        """

        return self.canonicalize_raw(
            evidence=evidence,
            canonical_evidence_id=canonical_evidence_id,
            provenance=provenance,
        )