from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema


PLAN_LIMITS = {
    "sandbox": {
        "max_public_claims": 3,
    },
    "starter": {
        "max_public_claims": 3,
    },
    "pro": {
        "max_public_claims": 50,
    },
    "growth": {
        "max_public_claims": 200,
    },
    "business": {
        "max_public_claims": 1000,
    },
}


def normalize_plan_code(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    return normalized if normalized in PLAN_LIMITS else "starter"


def get_workspace_limits(plan_code: str):
    normalized = normalize_plan_code(plan_code)
    return PLAN_LIMITS.get(normalized, PLAN_LIMITS["starter"])


def get_workspace_usage(workspace_id: int, db: Session):
    public_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.visibility == "public",
            ClaimSchema.status.in_(["published", "locked"]),
        )
        .count()
    )

    locked_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status == "locked",
        )
        .count()
    )

    return {
        "public_claims": public_claims,
        "locked_claims": locked_claims,
    }


def can_create_public_claim(workspace_id: int, effective_plan_code: str, db: Session):
    limits = get_workspace_limits(effective_plan_code)
    usage = get_workspace_usage(workspace_id, db)

    return usage["public_claims"] < limits["max_public_claims"]