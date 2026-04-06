from sqlalchemy.orm import Session
from app.models.claim_schema import ClaimSchema
from app.models.workspace import Workspace
from app.api.routes.billing import resolve_effective_plan_code


PLAN_LIMITS = {
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


def get_workspace_limits(plan: str):
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["starter"])


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


def can_create_public_claim(workspace: Workspace, db: Session):
    effective_plan = resolve_effective_plan_code(workspace)
    limits = get_workspace_limits(effective_plan)
    usage = get_workspace_usage(workspace.id, db)

    return usage["public_claims"] < limits["max_public_claims"]