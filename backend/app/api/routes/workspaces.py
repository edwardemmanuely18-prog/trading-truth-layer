from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.workspace import Workspace
from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership
from app.api.deps import get_current_user

router = APIRouter()


def require_workspace_member(workspace_id: int, current_user: User, db: Session):
    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(status_code=403, detail="User is not a member of this workspace")

    return membership


def serialize_workspace_member(membership: WorkspaceMembership, user: User):
    return {
        "workspace_id": membership.workspace_id,
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "global_role": user.role,
        "workspace_role": membership.role,
    }


@router.get("/workspaces/{workspace_id}/dashboard")
def get_workspace_dashboard(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_member(workspace_id, current_user, db)

    member_ids = db.query(Trade.member_id).filter(Trade.workspace_id == workspace_id).distinct().all()
    trade_count = db.query(Trade).filter(Trade.workspace_id == workspace_id).count()
    claim_count = db.query(ClaimSchema).filter(ClaimSchema.workspace_id == workspace_id).count()

    return {
        "workspace_id": workspace.id,
        "workspace_name": workspace.name,
        "member_count": len(member_ids),
        "trade_count": trade_count,
        "claim_count": claim_count,
    }


@router.get("/workspaces/{workspace_id}/members")
def list_workspace_members(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_member(workspace_id, current_user, db)

    rows = (
        db.query(WorkspaceMembership, User)
        .join(User, User.id == WorkspaceMembership.user_id)
        .filter(WorkspaceMembership.workspace_id == workspace_id)
        .order_by(WorkspaceMembership.id.asc())
        .all()
    )

    return [serialize_workspace_member(membership, user) for membership, user in rows]