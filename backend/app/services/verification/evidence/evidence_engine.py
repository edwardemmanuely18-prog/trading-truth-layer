from __future__ import annotations

from app.services.verification.verification_models import (
    ComponentResult,
)

from app.services.verification.scoring_weights import (
    EVIDENCE_AUTHENTICITY,
)

from app.services.verification.intelligence.verification_tiers import (
    authenticity_points,
)

from app.services.verification.evidence.broker_provenance_engine import (
    build_claim_provenance,
)

from app.services.verification.verification_context import (
    VerificationContext,
)


# ============================================================
# SCORING HELPERS
# ============================================================

def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def ratio(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return count / total


def compute_evidence_score(
    context: VerificationContext,
) -> ComponentResult:

    provenance = build_claim_provenance(
        context.trades
    )

    if provenance.total_trades == 0:

        return ComponentResult(

            name="Evidence Authenticity",

            earned_points=0,

            maximum_points=EVIDENCE_AUTHENTICITY,

            status="Unavailable",

            reason="No trades available.",

        )

    # --------------------------------------------------------
    # Tier composition
    # --------------------------------------------------------

    tier1_ratio = ratio(
        provenance.tier1_count,
        provenance.total_trades,
    )

    tier2_ratio = ratio(
        provenance.tier2_count,
        provenance.total_trades,
    )

    tier3_ratio = ratio(
        provenance.tier3_count,
        provenance.total_trades,
    )

    # --------------------------------------------------------
    # Manual modifications
    # --------------------------------------------------------

    manual_count = sum(
        1
        for trade in provenance.trades
        if trade.manually_modified
    )

    manual_ratio = ratio(
        manual_count,
        provenance.total_trades,
    )

    # --------------------------------------------------------
    # Tier Quality (0–8)
    # --------------------------------------------------------

    average_authenticity = sum(
        authenticity_points(t.verification_tier)
        for t in provenance.trades
    ) / provenance.total_trades

    tier_quality = (
        average_authenticity / 30.0
    ) * 8.0

    # --------------------------------------------------------
    # Consistency (0–3)
    # --------------------------------------------------------

    dominant_ratio = max(
        tier1_ratio,
        tier2_ratio,
        tier3_ratio,
    )

    consistency = dominant_ratio * 3.0

    # --------------------------------------------------------
    # Integrity (0–2)
    # --------------------------------------------------------

    integrity = max(
        0.0,
        2.0 - (manual_ratio * 2.0),
    )

    # --------------------------------------------------------
    # Sample Confidence (0–2)
    # --------------------------------------------------------

    trades = provenance.total_trades

    if trades >= 100:
        sample = 2.0

    elif trades >= 50:
        sample = 1.5

    elif trades >= 20:
        sample = 1.0

    elif trades >= 10:
        sample = 0.75

    else:
        sample = 0.50

    # --------------------------------------------------------
    # Final Score
    # --------------------------------------------------------

    earned = round(
        clamp(
            tier_quality
            + consistency
            + integrity
            + sample,
            0.0,
            EVIDENCE_AUTHENTICITY,
        ),
        2,
    )

    return ComponentResult(

        name="Evidence Authenticity",

        earned_points=earned,

        maximum_points=EVIDENCE_AUTHENTICITY,

        status=provenance.primary_tier,

        reason=(
            "Derived from verified "
            "trade provenance."
        ),

        details={

            "primary_tier":
                provenance.primary_tier,

            "primary_source":
                provenance.primary_source,

            "trade_count":
                provenance.total_trades,

            "tier1_count":
                provenance.tier1_count,

            "tier2_count":
                provenance.tier2_count,

            "tier3_count":
                provenance.tier3_count,

            "tier1_ratio":
                round(tier1_ratio, 4),

            "tier2_ratio":
                round(tier2_ratio, 4),

            "tier3_ratio":
                round(tier3_ratio, 4),

            "manual_trade_count":
                manual_count,

            "manual_trade_ratio":
                round(manual_ratio, 4),

            "tier_quality_score":
                round(tier_quality, 2),

            "consistency_score":
                round(consistency, 2),

            "integrity_score":
                round(integrity, 2),

            "sample_confidence_score":
                round(sample, 2),

            "penalties": {

                "manual_edit_penalty":
                    round(manual_ratio * 2.0, 2),

            },

        },

    )