import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership


def workspace_limits_disabled() -> bool:
    raw = os.getenv("DISABLE_WORKSPACE_LIMITS", "false").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def get_workspace_limit_snapshot(db: Session, workspace_id: int) -> dict:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found.")

    member_used = (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id)
        .count()
    )
    trade_used = db.query(Trade).filter(Trade.workspace_id == workspace_id).count()
    claim_used = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.workspace_id == workspace_id)
        .count()
    )

    member_limit = workspace.member_limit or 0
    trade_limit = workspace.trade_limit or 0
    claim_limit = workspace.claim_limit or 0
    storage_limit_mb = workspace.storage_limit_mb or 0

    return {
        "workspace_id": workspace_id,
        "limits_disabled": workspace_limits_disabled(),
        "usage": {
            "members": {
                "used": member_used,
                "limit": member_limit,
            },
            "trades": {
                "used": trade_used,
                "limit": trade_limit,
            },
            "claims": {
                "used": claim_used,
                "limit": claim_limit,
            },
            "storage_mb": {
                "used": 0,
                "limit": storage_limit_mb,
            },
        },
    }


def enforce_workspace_claim_limit(db: Session, workspace_id: int) -> None:
    snapshot = get_workspace_limit_snapshot(db, workspace_id)

    if snapshot["limits_disabled"]:
        return

    used = snapshot["usage"]["claims"]["used"]
    limit = snapshot["usage"]["claims"]["limit"]

    if limit > 0 and used >= limit:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Claim limit reached for workspace {workspace_id}. "
                f"Current claims: {used}. Plan limit: {limit}. "
                f"Upgrade workspace plan to create additional claims."
            ),
        )


def enforce_workspace_trade_limit(db: Session, workspace_id: int, incoming_rows: int = 1) -> None:
    snapshot = get_workspace_limit_snapshot(db, workspace_id)

    if snapshot["limits_disabled"]:
        return

    used = snapshot["usage"]["trades"]["used"]
    limit = snapshot["usage"]["trades"]["limit"]

    if limit > 0 and (used + incoming_rows) > limit:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Trade limit reached for workspace {workspace_id}. "
                f"Current trades: {used}. Incoming rows: {incoming_rows}. "
                f"Plan limit: {limit}. Upgrade workspace plan to import additional trades."
            ),
        )


def enforce_workspace_member_limit(db: Session, workspace_id: int, incoming_members: int = 1) -> None:
    snapshot = get_workspace_limit_snapshot(db, workspace_id)

    if snapshot["limits_disabled"]:
        return

    used = snapshot["usage"]["members"]["used"]
    limit = snapshot["usage"]["members"]["limit"]

    if limit > 0 and (used + incoming_members) > limit:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Member limit reached for workspace {workspace_id}. "
                f"Current members: {used}. Incoming members: {incoming_members}. "
                f"Plan limit: {limit}. Upgrade workspace plan to invite additional members."
            ),
        )