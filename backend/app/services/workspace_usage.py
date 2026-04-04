from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema


PLAN_LIMITS = {
    "starter": {
        "max_public_claims": 3,
    },
    "pro": {
        "max_public_claims": 50,
    },
    "growth": {
        "max_public_claims": 150,
    },
    "business": {
        "max_public_claims": 500,
    },
}


def normalize_plan_code(plan_code: str | None) -> str:
    value = str(plan_code or "").strip().lower()
    if value in PLAN_LIMITS:
        return value
    return "starter"


def get_workspace_limits(plan_code: str):
    normalized = normalize_plan_code(plan_code)
    return PLAN_LIMITS[normalized]


def get_workspace_usage(workspace_id: int, db: Session):
    public_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.visibility.in_(["public", "unlisted"]),
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


def can_create_public_claim(workspace_id: int, plan_code: str, db: Session):
    limits = get_workspace_limits(plan_code)
    usage = get_workspace_usage(workspace_id, db)
    return usage["public_claims"] < limits["max_public_claims"]