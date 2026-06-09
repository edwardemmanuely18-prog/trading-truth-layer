from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.user import User
from app.models.workspace import Workspace
from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.workspace_membership import WorkspaceMembership

from app.api.deps import require_platform_owner

router = APIRouter(
    prefix="/aurum",
    tags=["Aurum Operations"]
)


@router.get("/overview")
def get_aurum_overview(
    current_user = Depends(require_platform_owner),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()

    verified_users = (
        db.query(User)
        .filter(User.email_verified == True)
        .count()
    )

    total_workspaces = (
        db.query(Workspace)
        .count()
    )

    internal_workspaces = (
        db.query(Workspace)
        .filter(
            Workspace.is_internal_workspace == 1
        )
        .count()
    )

    total_memberships = (
        db.query(WorkspaceMembership)
        .count()
    )

    total_claims = (
        db.query(ClaimSchema)
        .count()
    )

    draft_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.status == "draft"
        )
        .count()
    )

    verified_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.status == "verified"
        )
        .count()
    )

    published_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.status == "published"
        )
        .count()
    )

    locked_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.status == "locked"
        )
        .count()
    )

    total_trades = (
        db.query(Trade)
        .count()
    )

    return {
        "total_users": total_users,
        "verified_users": verified_users,

        "total_workspaces": total_workspaces,
        "internal_workspaces": internal_workspaces,

        "total_memberships": total_memberships,

        "total_claims": total_claims,
        "draft_claims": draft_claims,
        "verified_claims": verified_claims,
        "published_claims": published_claims,
        "locked_claims": locked_claims,

        "total_trades": total_trades,
    }


@router.get("/users")
def get_aurum_users(
    current_user = Depends(require_platform_owner),
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "email_verified": u.email_verified,
            "created_at": (
                u.created_at.isoformat()
                if u.created_at
                else None
            ),
        }
        for u in users
    ]