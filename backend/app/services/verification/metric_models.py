from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.services.verification.verification_models import (
    ComponentResult,
)


# ============================================================
# CLAIM VERIFICATION METRICS
# ============================================================

@dataclass(slots=True)
class ClaimVerificationMetrics:
    """
    Canonical verification metrics for a single ClaimSchema.

    Every single-claim verification surface
    consumes this object.

    Examples:

    - Claim Report PDF
    - Verify Page
    - Public Claim Page
    - Claim API
    """

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    claim_schema_id: int

    workspace_id: int

    claim_hash: str | None

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    verification_score: float

    verification_band: str

    verification_tier: str

    verification_status: str

    # --------------------------------------------------------
    # Institutional Evidence Profile
    # --------------------------------------------------------

    primary_tier: str

    primary_source: str

    tier1_count: int

    tier2_count: int

    tier3_count: int

    tier1_percent: float

    tier2_percent: float

    tier3_percent: float

    # --------------------------------------------------------
    # TVS Components
    # --------------------------------------------------------

    evidence: ComponentResult

    integrity: ComponentResult

    governance: ComponentResult

    transparency: ComponentResult

    stability: ComponentResult

    network: ComponentResult

    reviews: ComponentResult

    disputes: ComponentResult

    # --------------------------------------------------------
    # Timeline
    # --------------------------------------------------------

    verified_at: datetime | None

    published_at: datetime | None

    locked_at: datetime | None

    # --------------------------------------------------------
    # Decision
    # --------------------------------------------------------

    decision: str

    confidence: float

    warnings: list[str] = field(
        default_factory=list
    )

    recommendations: list[str] = field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Trading Performance
    # --------------------------------------------------------

    claim_trade_count: int = 0

    performance_metrics: dict[str, Any] = field(
        default_factory=dict
    )

    # --------------------------------------------------------
    # Identity Projection
    # --------------------------------------------------------

    identity: dict[str, Any] = field(
        default_factory=dict
    )

    qr_payload: dict[str, Any] = field(
        default_factory=dict
    )

    # --------------------------------------------------------
    # Extension Point
    # --------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# WORKSPACE VERIFICATION METRICS
# ============================================================

@dataclass(slots=True)
class WorkspaceVerificationMetrics:
    """
    Canonical workspace verification metrics.

    Aggregated ONLY from VerificationCertificates.

    No verification is computed here.

    This object is consumed by:

    - Allocator Report
    - Workspace Dashboard
    - Workspace APIs
    """

    workspace_id: int

    claim_count: int

    draft_claim_count: int

    verified_claim_count: int

    published_claim_count: int

    locked_claim_count: int

    verification_coverage: float

    average_verification_score: float

    verification_band: str

    evidence: ComponentResult

    integrity: ComponentResult

    governance: ComponentResult

    transparency: ComponentResult

    stability: ComponentResult

    network: ComponentResult

    reviews: ComponentResult

    disputes: ComponentResult

    status_distribution: dict[str, int] = field(
        default_factory=dict,
    )

    decision_distribution: dict[str, int] = field(
        default_factory=dict,
    )

    band_distribution: dict[str, int] = field(
        default_factory=dict,
    )

    tier_distribution: dict[str, int] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )