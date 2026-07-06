from __future__ import annotations

from app.services.verification.verification_context import (
    VerificationContext,
)

from app.services.verification.verification_models import (
    ComponentResult,
)

from app.services.verification.scoring_weights import (
    DISPUTE_RESOLUTION,
)


def compute_dispute_score(
    context: VerificationContext,
) -> ComponentResult:

    disputes = context.disputes

    total_disputes = len(disputes)

    open_count = 0
    resolved_count = 0
    dismissed_count = 0

    for dispute in disputes:

        status = str(

            getattr(
                dispute,
                "status",
                "",
            )

        ).lower()

        if status == "open":

            open_count += 1

        elif status in {

            "resolved",
            "closed",
            "accepted",

        }:

            resolved_count += 1

        else:

            dismissed_count += 1

    #
    # ------------------------------------------
    # Progressive deduction
    # ------------------------------------------
    #

    deduction = 0.0

    deduction += open_count * 2.0

    deduction += dismissed_count * 0.50

    deduction -= resolved_count * 0.25

    deduction = max(
        deduction,
        0.0,
    )

    earned = max(

        0.0,

        round(

            DISPUTE_RESOLUTION
            - deduction,

            2,

        ),

    )

    if earned >= 7:

        status = "Clear"

    elif earned >= 5:

        status = "Minor Concerns"

    elif earned >= 3:

        status = "Moderate Risk"

    else:

        status = "High Risk"

    details = {

        "total_disputes":
            total_disputes,

        "open_disputes":
            open_count,

        "resolved_disputes":
            resolved_count,

        "dismissed_disputes":
            dismissed_count,

        "deduction":
            deduction,

    }

    return ComponentResult(

        name="Dispute Resolution",

        earned_points=earned,

        maximum_points=DISPUTE_RESOLUTION,

        status=status,

        reason=(

            "Computed from canonical "
            "claim dispute history."

        ),

        details=details,

    )