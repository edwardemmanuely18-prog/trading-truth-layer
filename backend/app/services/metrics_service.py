from sqlalchemy.orm import Session
from app.models.trade import Trade
from app.models.workspace import Workspace


def get_workspace_trade_metrics(db: Session, workspace_id: int) -> dict:
    trades = db.query(Trade).filter(
        Trade.workspace_id == workspace_id
    ).all()

    total = len(trades)

    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id
    ).first()

    # ✅ USE TRUE CONSUMPTION (NOT CURRENT COUNT)
    used = workspace.trades_consumed_count or 0

    limit = workspace.trade_limit if workspace else 200

    wins = 0
    losses = 0
    total_pnl = 0

    for t in trades:
        pnl = t.net_pnl or 0
        total_pnl += pnl

        if pnl > 0:
            wins += 1
        elif pnl < 0:
            losses += 1

    win_rate = (wins / total * 100) if total > 0 else 0
    utilization = (used / limit * 100) if limit > 0 else 0

    return {
    "used": used,  # 🔒 FIX: must be lifetime consumption

    "consumed": used,  # optional alias (same thing)

    "limit": limit,
    "utilization": round(utilization, 2),

    "ledger_count": total,  # 📊 real trades in DB

    "win_rate": round(win_rate, 2),
    "total_pnl": round(total_pnl, 2),
    "wins": wins,
    "losses": losses,
}