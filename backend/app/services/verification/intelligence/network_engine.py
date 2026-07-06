from __future__ import annotations

from app.services.verification.verification_context import (
    VerificationContext,
)

from app.services.verification.verification_models import (
    ComponentResult,
)

from app.services.verification.scoring_weights import (
    VERIFICATION_NETWORK,
)

from app.services.verification.evidence.broker_provenance_engine import (
    build_claim_provenance,
)


def compute_network_score(
    context: VerificationContext,
) -> ComponentResult:
    """
    Measures how much of the verification
    process has been independently validated
    through Trading Truth Layer infrastructure.

    This component is intentionally independent
    from profitability.
    """

    provenance = build_claim_provenance(
        context.trades
    )

    #
    # -----------------------------------------
    # Registry Coverage (2)
    # -----------------------------------------
    #

    evidence_count = len(
        context.evidence_records
    )

    if evidence_count >= 3:
        registry_score = 2.0

    elif evidence_count >= 1:
        registry_score = 1.0

    else:
        registry_score = 0.0

    #
    # -----------------------------------------
    # Broker Provenance (2)
    # -----------------------------------------
    #

    if provenance.primary_tier == "tier_1":
        broker_score = 2.0

    elif provenance.primary_tier == "tier_2":
        broker_score = 1.5

    elif provenance.primary_tier == "tier_3":
        broker_score = 1.0

    else:
        broker_score = 0.0

    #
    # -----------------------------------------
    # Integrity Participation (2)
    # -----------------------------------------
    #

    integrity_score = 0.0

    if context.integrity_scan:

        integrity_score += 1.0

        if len(context.integrity_alerts) == 0:
            integrity_score += 1.0

    #
    # -----------------------------------------
    # Public Verification (2)
    # -----------------------------------------
    #

    claim = context.claim_schema

    public_score = 0.0

    if getattr(
        claim,
        "claim_hash",
        None,
    ):
        public_score += 0.5

    if getattr(
        claim,
        "verified_at",
        None,
    ):
        public_score += 0.5

    if getattr(
        claim,
        "published_at",
        None,
    ):
        public_score += 0.5

    if getattr(
        claim,
        "locked_at",
        None,
    ):
        public_score += 0.5

    earned = round(

        registry_score
        + broker_score
        + integrity_score
        + public_score,

        2,

    )

    earned = min(
        earned,
        VERIFICATION_NETWORK,
    )

    details = {

        "registry_score":
            registry_score,

        "broker_score":
            broker_score,

        "integrity_score":
            integrity_score,

        "public_score":
            public_score,

        "evidence_records":
            evidence_count,

        "primary_tier":
            provenance.primary_tier,

    }

    if earned >= 7:

        status = "Institutional"

    elif earned >= 5:

        status = "Strong"

    elif earned >= 3:

        status = "Moderate"

    else:

        status = "Limited"

    return ComponentResult(

        name="Verification Network",

        earned_points=earned,

        maximum_points=VERIFICATION_NETWORK,

        status=status,

        reason=(
            "Derived from verification "
            "infrastructure."
        ),

        details=details,

    )