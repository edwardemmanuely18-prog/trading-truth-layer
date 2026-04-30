from sqlalchemy.orm import Session
from app.models.trade import Trade


def get_workspace_trade_metrics(db: Session, workspace_id: int) -> dict:
    """
    Compute trade usage metrics for a workspace.
    This is the single source of truth for capacity.
    """

    total_trades = db.query(Trade).filter(
        Trade.workspace_id == workspace_id,
        Trade.deleted_at.is_(None)  # ignore soft-deleted trades
    ).count()

    # Default plan limit (you can later move this to billing config)
    limit = 200

    utilization = (total_trades / limit * 100) if limit > 0 else 0

    return {
        "used": total_trades,
        "limit": limit,
        "utilization": round(utilization, 2),
    }