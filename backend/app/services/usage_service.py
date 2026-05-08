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
    from app.models.workspace import Workspace

    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id)
        .first()
    )

    # ACTIVE ledger trades (mutable)
    active_trade_count = (
        db.query(func.count(Trade.id))
        .filter(Trade.workspace_id == workspace_id)
        .scalar()
    )

    # GOVERNANCE COUNT (never decreases)
    from app.models.workspace import Workspace

    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id)
        .first()
    )

    consumed_trade_count = int(
        getattr(workspace, "trades_consumed_count", 0) or 0
    )

    # LIVE LEDGER ROWS (decreases on delete)
    ledger_trade_count = (
        db.query(func.count(Trade.id))
        .filter(Trade.workspace_id == workspace_id)
        .scalar()
    )

    ledger_trade_count = ledger_trade_count or 0

    return {
        "claims": claim_count or 0,
        "trades": consumed_trade_count,
        "ledger_trades": ledger_trade_count,
        "members": member_count or 0,
    }