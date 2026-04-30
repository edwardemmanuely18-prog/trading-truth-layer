from sqlalchemy.orm import Session
from app.models.trade import Trade


def get_workspace_trade_metrics(db: Session, workspace_id: int) -> dict:
    """
    Computes trade usage and performance metrics for a workspace.
    This is the single source of truth for:
    - Trade capacity (used / limit)
    - Performance (PnL, win rate)
    """

    # ---- Fetch trades ----
    trades = db.query(Trade).filter(
        Trade.workspace_id == workspace_id
    ).all()

    total = len(trades)

    # ---- Config (can later come from plan/entitlements) ----
    limit = 200

    # ---- Initialize metrics ----
    wins = 0
    losses = 0
    breakeven = 0

    total_pnl = 0.0
    gross_profit = 0.0
    gross_loss = 0.0

    quantities = 0.0

    # ---- Compute metrics ----
    for t in trades:
        pnl = float(t.net_pnl or 0)
        qty = float(t.quantity or 0)

        total_pnl += pnl
        quantities += qty

        if pnl > 0:
            wins += 1
            gross_profit += pnl
        elif pnl < 0:
            losses += 1
            gross_loss += pnl
        else:
            breakeven += 1

    # ---- Derived metrics ----
    win_rate = (wins / total * 100) if total > 0 else 0
    loss_rate = (losses / total * 100) if total > 0 else 0

    avg_pnl = (total_pnl / total) if total > 0 else 0

    profit_factor = (
        abs(gross_profit / gross_loss)
        if gross_loss != 0
        else None
    )

    utilization = (total / limit * 100) if limit > 0 else 0

    # ---- Final response ----
    return {
        "used": total,
        "limit": limit,
        "utilization": round(utilization, 2),

        "performance": {
            "total_pnl": round(total_pnl, 2),
            "avg_pnl": round(avg_pnl, 2),
            "win_rate": round(win_rate, 2),
            "loss_rate": round(loss_rate, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor else None,
        },

        "distribution": {
            "wins": wins,
            "losses": losses,
            "breakeven": breakeven,
        },

        "volume": {
            "total_quantity": round(quantities, 4),
        }
    }