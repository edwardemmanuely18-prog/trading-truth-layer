from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.claim_schema import ClaimSchema
from app.models.review_statement import ReviewStatement

router = APIRouter(
    prefix="/trust-scores",
    tags=["Trust Scores"],
)


@router.get(
    "/workspace/{workspace_id}"
)
def get_workspace_trust_scores(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    results = []

    for claim in claims:

        score = 0

        status = (
            claim.status or ""
        ).lower()

        if status == "verified":
            score += 25

        elif status == "published":
            score += 40

        elif status == "locked":
            score += 60

        reviews = (
            db.query(
                ReviewStatement
            )
            .filter(
                ReviewStatement.claim_schema_id
                == claim.id
            )
            .all()
        )

        review_count = len(reviews)

        for review in reviews:

            if review.review_direction == "POSITIVE":
                score += 3

            elif review.review_direction == "NEGATIVE":
                score -= 15

            elif review.review_direction == "CRITICAL":
                score -= 35

        avg_rating = (
            round(
                sum(
                    r.rating or 0
                    for r in reviews
                ) / review_count,
                2
            )
            if review_count > 0
            else 0
        )

        score = round(
            min(score, 100),
            2,
        )

        tier = "REVIEW REQUIRED"

        if score >= 90:
            tier = "INSTITUTIONAL GRADE"

        elif score >= 75:
            tier = "VERIFIED"

        elif score >= 60:
            tier = "MONITORED"

        elif score >= 40:
            tier = "REVIEW REQUIRED"

        else:
            tier = "HIGH RISK"

        results.append(
            {
                "claim_id":
                    claim.id,

                "claim_name":
                    claim.name,

                "status":
                    claim.status,

                "trust_score":
                    score,

                "review_count":
                    review_count,

                "average_rating":
                    round(
                        avg_rating,
                        2,
                    ),

                "tier":
                    tier,
            }
        )

    results.sort(
        key=lambda x:
        x["trust_score"],
        reverse=True,
    )

    return {
        "count":
            len(results),

        "scores":
            results,
    }