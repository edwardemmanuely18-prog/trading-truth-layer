from __future__ import annotations

from app.services.verification.verification_context import (
    VerificationContext,
)

from app.services.verification.verification_models import (
    ComponentResult,
)

from app.services.verification.scoring_weights import (
    INDEPENDENT_REVIEW,
)


def compute_review_score(
    context: VerificationContext,
) -> ComponentResult:
    """
    Independent review component.

    This engine is intentionally future-proof.

    Today it can consume manually entered
    institutional reviews.

    Tomorrow it can consume:

    - Prop Firms
    - Brokers
    - Auditors
    - Regulators
    """

    reviews = context.review_statements

    review_count = len(
        reviews
    )

    if review_count == 0:

        earned = 0.0

        status = "Unavailable"

        confidence = 0.0

    else:

        confidence_values = []

        positive = 0

        neutral = 0

        negative = 0

        for review in reviews:

            #
            # Preferred:
            # explicit confidence field
            #

            value = getattr(
                review,
                "confidence",
                None,
            )

            if value is not None:

                confidence_values.append(
                    float(value)
                )

                continue

            #
            # Fallback:
            # sentiment/status
            #

            sentiment = str(

                getattr(
                    review,
                    "status",
                    "",
                )

            ).lower()

            if sentiment in {

                "approved",
                "verified",
                "accepted",
                "positive",

            }:

                confidence_values.append(
                    100
                )

                positive += 1

            elif sentiment in {

                "neutral",
                "pending",

            }:

                confidence_values.append(
                    60
                )

                neutral += 1

            else:

                confidence_values.append(
                    20
                )

                negative += 1

        confidence = (

            sum(confidence_values)

            /

            len(confidence_values)

        )

        earned = round(

            confidence
            / 100

            * INDEPENDENT_REVIEW,

            2,

        )

        if earned >= 7:

            status = "Institutional"

        elif earned >= 5:

            status = "Strong"

        elif earned >= 3:

            status = "Moderate"

        else:

            status = "Limited"

    details = {

        "review_count":
            review_count,

        "average_confidence":
            round(
                confidence,
                2,
            ),

    }

    return ComponentResult(

        name="Independent Review",

        earned_points=earned,

        maximum_points=INDEPENDENT_REVIEW,

        status=status,

        reason=(

            "Computed from canonical "
            "review statements."

        ),

        details=details,

    )