from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from app.services.verification.verification_models import (
    EvidenceLineage,
    EvidenceLineageStep,
)

from app.services.verification.verification_constants import (
    TIER_1,
    TIER_2,
    TIER_3,
    SOURCE_MANUAL,
    SOURCE_BROKER_CSV,
    SOURCE_BROKER_FLEX,
    LIVE_SOURCES,
)


# ============================================================
# Trade Provenance
# ============================================================

@dataclass(slots=True)
class TradeProvenance:

    trade_id: int | None

    evidence_source: str

    verification_tier: str

    original_verification_tier: str

    manually_modified: bool

    downgrade_reason: str | None = None

    lineage: EvidenceLineage | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# Claim Provenance
# ============================================================

from app.services.verification.verification_models import (
    TierComposition,
)

@dataclass(slots=True)
class ClaimProvenance:

    trades: list[TradeProvenance]

    primary_tier: str

    primary_source: str

    tier1_count: int

    tier2_count: int

    tier3_count: int

    total_trades: int

    tier_composition: TierComposition

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# Tier Resolution
# ============================================================

def resolve_trade_tier(
    trade: Any,
) -> TradeProvenance:

    source = str(
        getattr(
            trade,
            "evidence_source",
            SOURCE_MANUAL,
        )
    ).lower()

    manually_modified = bool(
        getattr(
            trade,
            "manually_modified",
            False,
        )
    )

    # --------------------------------------------------------
    # Immutable downgrade rule
    # --------------------------------------------------------

    if manually_modified:

        return TradeProvenance(

            trade_id=getattr(trade, "id", None),

            evidence_source=source,

            verification_tier=TIER_3,

            original_verification_tier=(
                determine_original_tier(source)
            ),

            manually_modified=True,

            downgrade_reason=(
                "Trade manually modified after import."
            ),

            lineage=build_trade_lineage(

                trade,

                source,

                TIER_3,

                True,

            ),

        )

    original = determine_original_tier(source)

    return TradeProvenance(

        trade_id=getattr(trade, "id", None),

        evidence_source=source,

        verification_tier=original,

        original_verification_tier=original,

        manually_modified=False,

        lineage=build_trade_lineage(

            trade,

            source,

            original,

            False,

        ),

    )


# ============================================================
# Source Classification
# ============================================================

def determine_original_tier(
    source: str,
) -> str:

    if source in LIVE_SOURCES:
        return TIER_1

    if source in {
        SOURCE_BROKER_CSV,
        SOURCE_BROKER_FLEX,
    }:
        return TIER_2

    return TIER_3


def build_trade_lineage(
    trade: Any,
    source: str,
    tier: str,
    manually_modified: bool,
) -> EvidenceLineage:

    lineage = EvidenceLineage(

        origin=source,

        current_state=tier,

    )

    lineage.steps.append(

        EvidenceLineageStep(

            event="origin",

            timestamp=getattr(
                trade,
                "opened_at",
                None,
            ),

            actor="broker",

            description="Trade originated from evidence source.",

        )

    )

    lineage.steps.append(

        EvidenceLineageStep(

            event="import",

            timestamp=getattr(
                trade,
                "created_at",
                None,
            ),

            actor="ttl",

            description="Trade imported into Trading Truth Layer.",

        )

    )

    if manually_modified:

        lineage.steps.append(

            EvidenceLineageStep(

                event="manual_edit",

                timestamp=datetime.utcnow(),

                actor="user",

                description=(
                    "Manual modification detected."
                ),

            )

        )

        lineage.immutable = False

    return lineage


# ============================================================
# Claim Aggregation
# ============================================================

def build_claim_provenance(
    trades: list[Any],
) -> ClaimProvenance:

    resolved = [
        resolve_trade_tier(t)
        for t in trades
    ]

    tier1 = sum(
        1
        for t in resolved
        if t.verification_tier == TIER_1
    )

    tier2 = sum(
        1
        for t in resolved
        if t.verification_tier == TIER_2
    )

    tier3 = sum(
        1
        for t in resolved
        if t.verification_tier == TIER_3
    )

    total = len(resolved)

    counts = {

        TIER_1: tier1,

        TIER_2: tier2,

        TIER_3: tier3,

    }

    primary_tier = max(
        counts,
        key=counts.get,
    )

    source_counts = {}

    for trade in resolved:

        source_counts[
            trade.evidence_source
        ] = (

            source_counts.get(
                trade.evidence_source,
                0,
            )
            + 1

        )

    primary_source = max(
        source_counts,
        key=source_counts.get,
        default=SOURCE_MANUAL,
    )

    composition = TierComposition(

        tier1_count=tier1,

        tier2_count=tier2,

        tier3_count=tier3,

        total_trades=total,

    )

    return ClaimProvenance(

        trades=resolved,

        primary_tier=primary_tier,

        primary_source=primary_source,

        tier1_count=tier1,

        tier2_count=tier2,

        tier3_count=tier3,

        total_trades=total,

        tier_composition=composition,

    )