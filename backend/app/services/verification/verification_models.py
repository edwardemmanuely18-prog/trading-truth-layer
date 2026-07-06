from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ============================================================
# TVS VERSION
# ============================================================

TVS_VERSION = "1.0"


# ============================================================
# COMPONENT RESULT
# ============================================================

@dataclass(slots=True)
class ComponentResult:
    """
    Canonical output for every verification component.
    """

    name: str

    earned_points: float

    maximum_points: float

    status: str

    reason: str = ""

    details: dict[str, Any] = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)

    recommendations: list[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:

        if self.maximum_points <= 0:
            return 0.0

        return round(
            self.earned_points
            / self.maximum_points
            * 100,
            2,
        )


# ============================================================
# EVIDENCE LINEAGE
# ============================================================

@dataclass(slots=True)
class EvidenceLineageStep:
    """
    One step in the evidence chain.
    """

    event: str

    timestamp: datetime | None = None

    actor: str | None = None

    description: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(slots=True)
class EvidenceLineage:
    """
    Complete provenance chain for one trade.
    """

    origin: str

    current_state: str

    steps: list[EvidenceLineageStep] = field(
        default_factory=list
    )

    immutable: bool = True


# ============================================================
# TIER COMPOSITION
# ============================================================

@dataclass(slots=True)
class TierComposition:

    tier1_count: int = 0

    tier2_count: int = 0

    tier3_count: int = 0

    total_trades: int = 0

    @property
    def tier1_percent(self) -> float:

        if self.total_trades == 0:
            return 0.0

        return round(
            self.tier1_count
            / self.total_trades
            * 100,
            2,
        )

    @property
    def tier2_percent(self) -> float:

        if self.total_trades == 0:
            return 0.0

        return round(
            self.tier2_count
            / self.total_trades
            * 100,
            2,
        )

    @property
    def tier3_percent(self) -> float:

        if self.total_trades == 0:
            return 0.0

        return round(
            self.tier3_count
            / self.total_trades
            * 100,
            2,
        )


# ============================================================
# VERIFICATION RESULT
# ============================================================

@dataclass(slots=True)
class VerificationResult:

    claim_id: int

    workspace_id: int

    tvs_version: str

    verification_score: float

    verification_band: str

    primary_verification_tier: str

    primary_evidence_source: str

    tier_composition: TierComposition

    components: dict[str, ComponentResult]

    lineage_summary: dict[str, Any] = field(
        default_factory=dict
    )

    warnings: list[str] = field(default_factory=list)

    recommendations: list[str] = field(default_factory=list)

    generated_at: datetime = field(
        default_factory=datetime.utcnow
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )