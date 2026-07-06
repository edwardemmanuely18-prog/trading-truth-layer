from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.review_statement import (
    ReviewStatement,
)

from app.models.claim_schema import (
    ClaimSchema,
)

from app.schemas.review_statement import (
    ReviewStatementCreate,
)

router = APIRouter(
    prefix="/external-reviews",
    tags=["External Reviews"],
)


@router.get(
    "/workspace/{workspace_id}"
)
def get_workspace_reviews(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    reviews = (
        db.query(ReviewStatement)
        .filter(
            ReviewStatement.workspace_id
            == workspace_id
        )
        .order_by(
            ReviewStatement.id.desc()
        )
        .all()
    )

    return {
        "count": len(reviews),

        "reviews": [
            {
                "id": r.id,

                "claim_schema_id":
                    r.claim_schema_id,

                "reviewer_name":
                    r.reviewer_name,

                "reviewer_organization":
                    r.reviewer_organization,

                "reviewer_role":
                    r.reviewer_role,

                "observation_type":
                    r.observation_type,

                "statement":
                    r.statement,

                "rating":
                    r.rating,

                "status":
                    r.status,

                "created_at":
                    r.created_at,
            }
            for r in reviews
        ],
    }


@router.get(
    "/claim/{claim_id}"
)
def get_claim_reviews(
    claim_id: int,
    db: Session = Depends(get_db),
):
    reviews = (
        db.query(ReviewStatement)
        .filter(
            ReviewStatement.claim_schema_id
            == claim_id
        )
        .order_by(
            ReviewStatement.id.desc()
        )
        .all()
    )

    return {
        "count": len(reviews),

        "reviews": [
            {
                "id": r.id,

                "reviewer_name":
                    r.reviewer_name,

                "reviewer_organization":
                    r.reviewer_organization,

                "reviewer_role":
                    r.reviewer_role,

                "observation_type":
                    r.observation_type,

                "statement":
                    r.statement,

                "rating":
                    r.rating,

                "status":
                    r.status,

                "created_at":
                    r.created_at,
            }
            for r in reviews
        ],
    }


@router.post(
    "/workspace/{workspace_id}"
)
def create_review(
    workspace_id: int,
    payload: ReviewStatementCreate,
    db: Session = Depends(get_db),
):
    statement = (
        payload.statement or ""
    ).lower()

    direction = "NEUTRAL"

    negative_terms = [
        "fraud",
        "fake",
        "manipulated",
        "incomplete",
        "missing",
        "invalid",
        "unverified",
        "risk",
        "loss",
        "drawdown",
        "poor",
        "low trust",
        "weak",
        "concern",
        "issue",
        "problem",
        "inconsistent",
        "unsupported",
        "failure",
        "misleading",
    ]

    positive_terms = [
        "verified",
        "validated",
        "reconciled",
        "consistent",
        "complete",
        "accurate",
        "confirmed",
        "institutional",
        "audited",
        "strong",
        "excellent",
        "credible",
        "trusted",
        "high quality",
        "well documented",
    ]

    claim = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.id
            == payload.claim_schema_id
        )
        .first()
    )

    negative_hits = sum(
        1
        for term in negative_terms
        if term in statement
    )

    positive_hits = sum(
        1
        for term in positive_terms
        if term in statement
    )

    if negative_hits >= 3:
        direction = "CRITICAL"

    elif negative_hits > positive_hits:
        direction = "NEGATIVE"

    elif positive_hits > negative_hits:
        direction = "POSITIVE"

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Claim not found",
        )

    allowed_statuses = {
        "verified",
        "published",
        "locked",
    }

    if (
        (claim.status or "").lower()
        not in allowed_statuses
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Reviews can only be submitted "
                "for VERIFIED, PUBLISHED or "
                "LOCKED claims."
            ),
        )

    rating = 5

    if direction == "POSITIVE":
        rating = 9

    elif direction == "NEGATIVE":
        rating = 4

    elif direction == "CRITICAL":
        rating = 1

    review = ReviewStatement(
        workspace_id=workspace_id,

        claim_schema_id=
            payload.claim_schema_id,

        reviewer_name=
            payload.reviewer_name,

        reviewer_organization=
            payload.reviewer_organization,

        reviewer_role=
            payload.reviewer_role,

        observation_type=
            payload.observation_type,

        statement=
            payload.statement,

        rating=
            rating,

        review_direction=
            direction,
    )

    db.add(review)

    db.commit()

    db.refresh(review)

    return {
        "review_id":
            review.id,

        "status":
            "created",
    }


@router.get(
    "/workspace/{workspace_id}/analytics"
)
def get_review_analytics(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    reviews = (
        db.query(ReviewStatement)
        .filter(
            ReviewStatement.workspace_id
            == workspace_id
        )
        .all()
    )

    role_counts = {}

    observation_counts = {}

    for review in reviews:

        role = (
            review.reviewer_role
            or "UNKNOWN"
        )

        observation = (
            review.observation_type
            or "UNKNOWN"
        )

        role_counts[role] = (
            role_counts.get(role, 0)
            + 1
        )

        observation_counts[
            observation
        ] = (
            observation_counts.get(
                observation,
                0,
            )
            + 1
        )

    return {
        "total_reviews":
            len(reviews),

        "roles":
            role_counts,

        "observation_types":
            observation_counts,
    }