from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.services.verification.verification_models import (
    ComponentResult,
    TierComposition,
)


# ============================================================
# CERTIFICATE IDENTITY
# ============================================================

@dataclass(slots=True)
class CertificateIdentity:
    """
    Immutable identity of a Verification Certificate.

    These values uniquely identify exactly what
    Trading Truth Layer certified.
    """

    certificate_id: str

    certificate_hash: str

    certificate_version: int

    tvs_version: str

    generated_at: datetime

    generated_by: str

    # --------------------------------------------------------
    # Canonical ClaimSchema identity
    # --------------------------------------------------------

    claim_schema_id: int

    claim_name: str

    workspace_id: int

    # --------------------------------------------------------
    # Existing ClaimSchema hashes
    # --------------------------------------------------------

    claim_hash: str | None = None

    scope_hash: str | None = None

    lifecycle_hash: str | None = None

    evidence_snapshot_hash: str | None = None

    locked_trade_set_hash: str | None = None


# ============================================================
# ISSUER
# ============================================================

@dataclass(slots=True)
class IssuerIdentity:
    """
    Workspace issuing this verification.
    """

    workspace_id: int

    workspace_name: str

    issuer_status: str

    issuer_rating: str | None = None

    verified_claims: int = 0

    verified_trades: int = 0

    average_verification_score: float = 0.0


# ============================================================
# SUMMARY
# ============================================================

@dataclass(slots=True)
class VerificationSummary:

    verification_score: float

    verification_band: str

    verification_tier: str

    evidence_tier: str

    verification_status: str

    integrity_status: str

    visibility: str

    trade_count: int

    verified_at: datetime | None = None

    published_at: datetime | None = None

    locked_at: datetime | None = None


# ============================================================
# COMPONENT SET
# ============================================================

@dataclass(slots=True)
class VerificationComponentSet:
    """
    Canonical TVS component collection.
    """

    evidence: ComponentResult

    integrity: ComponentResult

    governance: ComponentResult

    transparency: ComponentResult

    stability: ComponentResult

    network: ComponentResult

    reviews: ComponentResult

    disputes: ComponentResult

    @property
    def total_score(self) -> float:

        return round(

            self.evidence.earned_points

            + self.integrity.earned_points

            + self.governance.earned_points

            + self.transparency.earned_points

            + self.stability.earned_points

            + self.network.earned_points

            + self.reviews.earned_points

            + self.disputes.earned_points,

            2,

        )


# ============================================================
# PROVENANCE
# ============================================================

@dataclass(slots=True)
class ProvenanceSummary:

    primary_source: str

    primary_tier: str

    tier_composition: TierComposition

    evidence_records: int

    broker_connections: int

    verified_evidence: int

    fingerprints_verified: int


# ============================================================
# LINEAGE
# ============================================================

@dataclass(slots=True)
class LineageSummary:
    """
    High-level summary of the evidence chain.
    """

    total_trades: int

    tier1_trades: int

    tier2_trades: int

    tier3_trades: int

    manually_modified_trades: int

    immutable_trades: int


# ============================================================
# TIMELINE
# ============================================================

@dataclass(slots=True)
class TimelineSummary:

    created_at: datetime | None = None

    verified_at: datetime | None = None

    published_at: datetime | None = None

    locked_at: datetime | None = None

    latest_activity_at: datetime | None = None

    total_events: int = 0


# ============================================================
# DECISION RECORD
# ============================================================

@dataclass(slots=True)
class VerificationDecision:

    decision: str

    confidence: float

    explanation: str

    strengths: list[str] = field(
        default_factory=list
    )

    weaknesses: list[str] = field(
        default_factory=list
    )

    recommendations: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )


# ============================================================
# CERTIFICATE METADATA
# ============================================================

@dataclass(slots=True)
class CertificateMetadata:

    engine_version: str

    tvs_version: str

    generated_in_seconds: float

    verification_standard: str = (
        "Trading Verification Standard"
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# VERIFICATION CERTIFICATE
# ============================================================

@dataclass(slots=True)
class VerificationCertificate:
    """
    Canonical verification artifact generated by
    the Trading Truth Layer Verification Engine.

    Every verification consumer inside TTL should
    consume this object instead of computing
    verification independently.
    """

    identity: CertificateIdentity

    issuer: IssuerIdentity

    summary: VerificationSummary

    provenance: ProvenanceSummary

    component_scores: VerificationComponentSet

    lineage: LineageSummary

    timeline: TimelineSummary

    decision: VerificationDecision

    metadata: CertificateMetadata

    evidence: dict[str, Any] = field(
        default_factory=dict
    )

    integrity: dict[str, Any] = field(
        default_factory=dict
    )

    governance: dict[str, Any] = field(
        default_factory=dict
    )

    network: dict[str, Any] = field(
        default_factory=dict
    )

    external_reviews: dict[str, Any] = field(
        default_factory=dict
    )

    disputes: dict[str, Any] = field(
        default_factory=dict
    )

    attachments: dict[str, Any] = field(
        default_factory=dict
    )

    links: dict[str, Any] = field(
        default_factory=dict
    )

    custom: dict[str, Any] = field(
        default_factory=dict
    )

    # ==========================================================
    # CONVENIENCE PROPERTIES
    # ==========================================================

    @property
    def verification_score(self) -> float:
        """
        Canonical verification score.
        """

        return self.summary.verification_score

    @property
    def verification_band(self) -> str:
        """
        Canonical verification band.
        """

        return self.summary.verification_band

    @property
    def verification_tier(self) -> str:
        """
        Canonical verification tier.
        """

        return self.summary.verification_tier

    @property
    def components(self) -> VerificationComponentSet:
        """
        Canonical TVS component collection.
        """

        return self.component_scores

    @property
    def verification_url(self) -> str | None:
        """
        Public verification URL.
        """

        return self.links.get(
            "verification_url"
        )

    @property
    def qr_payload(self) -> str | None:
        """
        QR payload.
        """

        return self.links.get(
            "qr_payload"
        )

    @property
    def qr_caption(self) -> str | None:
        """
        QR caption.
        """

        return self.links.get(
            "qr_caption"
        )