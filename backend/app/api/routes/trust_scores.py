from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db

from app.services.verification.verification_service import (
    get_workspace_claim_verification_certificates,
    get_workspace_verification_metrics,
)



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
    certificates = (
        get_workspace_claim_verification_certificates(
            db=db,
            workspace_id=workspace_id,
            include_draft=True,
        )
    )

    workspace_metrics = (
        get_workspace_verification_metrics(
            db=db,
            workspace_id=workspace_id,
            include_draft=True,
        )
    )

    results = []

    for certificate in certificates:

        identity = (
            certificate.identity
        )

        summary = (
            certificate.summary
        )

        decision = (
            certificate.decision
        )

        external_reviews = (
            certificate.external_reviews
        )

        results.append(

            {

                "claim_id":
                    identity.claim_schema_id,

                "claim_name":
                    identity.claim_name,

                "status":
                    summary.verification_status,

                "trust_score":
                    summary.verification_score,

                "review_count":
                    external_reviews.get(
                        "reviews",
                        0,
                    ),

                "average_rating":
                    decision.confidence,

                "tier":
                    summary.verification_band,

            }

        )

    return {

        "summary": {

            "claims":
                workspace_metrics.claim_count,

            "average_score":
                workspace_metrics.average_verification_score,

            "institutional_grade":
                workspace_metrics.verification_band,

            "verified":
                workspace_metrics.locked_claim_count,

            "network_score":
                workspace_metrics.network.percentage,

        },

        "count":
            len(results),

        "scores":
            sorted(
                results,
                key=lambda x: x["trust_score"],
                reverse=True,
            ),

    }