from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema
from app.models.workspace import Workspace

from app.api.routes.billing import (
    resolve_effective_plan_code,
    get_workspace_plan_snapshot,
)


def normalize_plan_code(value: str | None) -> str:
    return str(value or "sandbox").strip().lower()


def get_workspace_usage(workspace_id: int, db: Session):
    """
    Unified governance usage service.

    ALL plan limits come from billing.py.
    No duplicated hardcoded limits allowed.
    """

    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id
    ).first()

    if not workspace:
        return {
            "public_claims": 0,
            "locked_claims": 0,
            "plan": "sandbox",
            "billing_active": False,
            "limit": 0,
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

    effective_plan_code = resolve_effective_plan_code(workspace)

    snapshot = get_workspace_plan_snapshot(
        effective_plan_code
    )

    return {

        "public_claims": public_claims,

        "locked_claims": locked_claims,

        "plan": effective_plan_code,

        "billing_active":
            workspace.billing_status == "active",

        "claim_limit":
            snapshot["claim_limit"],

        "trade_limit":
            snapshot["trade_limit"],

        "member_limit":
            snapshot["member_limit"],

        "storage_limit_mb":
            snapshot["storage_limit_mb"],

        "effective_plan_code":
            effective_plan_code,

    }


def can_create_public_claim(
    workspace_id: int,
    effective_plan_code: str,
    db: Session,
):
    """
    Disabled enforcement hook.
    """
    return True

