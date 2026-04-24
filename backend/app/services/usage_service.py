from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.workspace_membership import WorkspaceMembership


def get_workspace_usage(db: Session, workspace_id: int):
    """
    Returns current usage snapshot for a workspace.

    IMPORTANT:
    - Claims count ONLY includes economically relevant claims
      (locked / published), NOT drafts.
    - Trades count includes all trades (used for plan enforcement).
    - Members count includes all active memberships.
    """

    # ✅ FIXED: Only count claims that consume capacity
    claim_count = (
        db.query(func.count(ClaimSchema.id))
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status.in_(["locked", "published"])  # <-- KEY FIX
        )
        .scalar()
    )

    # Trades always count fully (no draft concept)
    trade_count = (
        db.query(func.count(Trade.id))
        .filter(Trade.workspace_id == workspace_id)
        .scalar()
    )

    # Members = total workspace memberships
    member_count = (
        db.query(func.count(WorkspaceMembership.id))
        .filter(WorkspaceMembership.workspace_id == workspace_id)
        .scalar()
    )

    return {
        "claims": claim_count or 0,
        "trades": trade_count or 0,
        "members": member_count or 0,
    }