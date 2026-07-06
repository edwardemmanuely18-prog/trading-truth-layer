from __future__ import annotations

from app.services.verification.verification_models import (
    ComponentResult,
)

from app.services.verification.scoring_weights import (
    GOVERNANCE,
)

from app.services.verification.verification_context import (
    VerificationContext,
)

from app.services.verification.verification_constants import (
    CLAIM_DRAFT,
    CLAIM_VERIFIED,
    CLAIM_PUBLISHED,
    CLAIM_LOCKED,
)


def compute_governance_score(
    context: VerificationContext,
) -> ComponentResult:

    status = str(
        getattr(
            context.claim_schema,
            "status",
            CLAIM_DRAFT,
        )
    ).lower()

    if status == CLAIM_LOCKED:

        earned = GOVERNANCE

    elif status == CLAIM_PUBLISHED:

        earned = round(
            GOVERNANCE * 0.85,
            2,
        )

    elif status == CLAIM_VERIFIED:

        earned = round(
            GOVERNANCE * 0.65,
            2,
        )

    else:

        earned = round(
            GOVERNANCE * 0.20,
            2,
        )

    return ComponentResult(

        name="Governance",

        earned_points=earned,

        maximum_points=GOVERNANCE,

        status=status.title(),

        reason=(
            "Derived from claim "
            "governance lifecycle."
        ),

        details={

            "claim_status": status,

            "audit_events":
                len(context.audit_events),

            "versions":
                len(context.claim_versions),

        },

    )