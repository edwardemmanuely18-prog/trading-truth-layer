from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema
from app.models.workspace import Workspace


def normalize_plan_code(value: str | None) -> str:
    return str(value or "sandbox").strip().lower()


def get_workspace_usage(workspace_id: int, db: Session):
    """
    Usage is now informational only.
    NO HARD LIMIT ENFORCEMENT HERE.
    """

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()

    if not workspace:
        return {
            "public_claims": 0,
            "locked_claims": 0,
            "plan": "sandbox",
            "billing_active": False,
            "limit": 1,
        }

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

    plan = normalize_plan_code(workspace.plan_code)
    billing_active = workspace.billing_status == "active"

    # STRICT FREE TIER LOGIC
    if plan == "sandbox":
        limit = 1  # allow ONLY 1 claim ever
    elif plan == "starter":
        limit = 5
    elif plan == "pro":
        limit = 50
    elif plan == "growth":
        limit = 200
    else:
        limit = 1000

    return {
        "public_claims": public_claims,
        "locked_claims": locked_claims,
        "plan": plan,
        "billing_active": billing_active,
        "limit": limit,
    }


def can_create_public_claim(workspace_id: int, effective_plan_code: str, db: Session):
    """
    DISABLED — kept only for backward compatibility.
    DO NOT USE THIS FOR ENFORCEMENT.
    """
    return True