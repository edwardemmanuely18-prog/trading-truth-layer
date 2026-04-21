from fastapi import HTTPException
from app.models.workspace import Workspace


def enforce_claim_limit(workspace: Workspace, current_count: int):
    if current_count >= workspace.claim_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Claim limit reached ({workspace.claim_limit}). Upgrade your plan."
        )


def enforce_trade_limit(workspace: Workspace, current_count: int):
    if current_count >= workspace.trade_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Trade limit reached ({workspace.trade_limit}). Upgrade your plan."
        )


def enforce_member_limit(workspace: Workspace, current_count: int):
    if current_count >= workspace.member_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Member limit reached ({workspace.member_limit}). Upgrade your plan."
        )