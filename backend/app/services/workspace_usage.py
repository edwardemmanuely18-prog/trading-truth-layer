from sqlalchemy.orm import Session
from app.models.claim_schema import ClaimSchema


FREE_LIMITS = {
    "max_public_claims": 3,
}


PRO_LIMITS = {
    "max_public_claims": 50,
}


def get_workspace_limits(plan: str):
    if plan == "pro":
        return PRO_LIMITS
    return FREE_LIMITS


def get_workspace_usage(workspace_id: int, db: Session):
    public_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.visibility == "public",
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


def can_create_public_claim(workspace_id: int, plan: str, db: Session):
    limits = get_workspace_limits(plan)
    usage = get_workspace_usage(workspace_id, db)

    return usage["public_claims"] < limits["max_public_claims"]