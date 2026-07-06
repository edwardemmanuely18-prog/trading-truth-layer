from __future__ import annotations

from app.services.verification.verification_models import (
    ComponentResult,
)

from app.services.verification.scoring_weights import (
    STABILITY,
)

from app.services.verification.verification_context import (
    VerificationContext,
)


def compute_stability_score(
    context: VerificationContext,
) -> ComponentResult:

    versions = max(
        len(context.claim_versions),
        1,
    )

    unlocks = sum(

        1

        for event in context.audit_events

        if "unlock"

        in str(event).lower()

    )

    verified = bool(
        context.claim_schema.verified_at
    )

    published = bool(
        context.claim_schema.published_at
    )

    locked = bool(
        context.claim_schema.locked_at
    )

    # --------------------------------------------------------
    # Version Stability (2)
    # --------------------------------------------------------

    version_score = max(

        0.0,

        2.0 - max(versions - 1, 0) * 0.50,

    )

    # --------------------------------------------------------
    # Unlock Stability (2)
    # --------------------------------------------------------

    unlock_score = max(

        0.0,

        2.0 - unlocks * 0.50,

    )

    # --------------------------------------------------------
    # Lifecycle Maturity (4)
    # --------------------------------------------------------

    lifecycle_score = 0.0

    if verified:
        lifecycle_score += 1.0

    if published:
        lifecycle_score += 1.5

    if locked:
        lifecycle_score += 1.5

    # --------------------------------------------------------
    # Final Stability Score
    # --------------------------------------------------------

    score = round(

        min(

            STABILITY,

            version_score
            + unlock_score
            + lifecycle_score,

        ),

        2,

    )

    return ComponentResult(

        name="Stability",

        earned_points=score,

        maximum_points=STABILITY,

        status="Stable",

        reason=(
            "Based on claim "
            "revision history."
        ),

        details={

            "versions": versions,

            "unlocks": unlocks,

            "verified": verified,

            "published": published,

            "locked": locked,

            "version_score": version_score,

            "unlock_score": unlock_score,

            "lifecycle_score": lifecycle_score,

        },

    )