from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.trade import Trade


def get_strategy_performance(db: Session, workspace_id: int):
    """
    Institutional-grade strategy analytics.

    Fixes:
    - Correct avg_win / avg_loss (separates win/loss pnl)
    - Accurate expectancy calculation
    - Safe null + zero handling
    """

    rows = (
        db.query(
            func.coalesce(Trade.strategy_tag, "unclassified").label("tag"),

            # core metrics
            func.count(Trade.id).label("trade_count"),
            func.coalesce(func.sum(Trade.net_pnl), 0).label("net_pnl"),
            func.coalesce(func.avg(Trade.net_pnl), 0).label("avg_pnl"),

            # win/loss counts
            func.sum(case((Trade.net_pnl > 0, 1), else_=0)).label("wins"),
            func.sum(case((Trade.net_pnl <= 0, 1), else_=0)).label("losses"),

            # 🔥 CRITICAL: separate pnl streams
            func.coalesce(
                func.sum(case((Trade.net_pnl > 0, Trade.net_pnl), else_=0)),
                0
            ).label("win_pnl"),

            func.coalesce(
                func.sum(case((Trade.net_pnl < 0, Trade.net_pnl), else_=0)),
                0
            ).label("loss_pnl"),
        )
        .filter(Trade.workspace_id == workspace_id)
        .group_by(Trade.strategy_tag)
        .all()
    )

    result = []

    for r in rows:
        total = int(r.trade_count or 0)
        wins = int(r.wins or 0)
        losses = int(r.losses or 0)

        net_pnl = float(r.net_pnl or 0)
        win_pnl = float(r.win_pnl or 0)
        loss_pnl = float(r.loss_pnl or 0)

        # --- core ratios ---
        win_rate = (wins / total) if total > 0 else 0.0

        # --- CORRECT averages ---
        avg_win = (win_pnl / wins) if wins > 0 else 0.0
        avg_loss = (loss_pnl / losses) if losses > 0 else 0.0  # negative value

        # --- EXPECTANCY (proper trading formula) ---
        expectancy = (
            (win_rate * avg_win) - ((1 - win_rate) * abs(avg_loss))
            if total > 0 else 0.0
        )

        result.append({
            "tag": r.tag or "unclassified",
            "trade_count": total,
            "net_pnl": net_pnl,
            "avg_pnl": float(r.avg_pnl or 0),

            "win_rate": float(win_rate),

            "avg_win": float(avg_win),
            "avg_loss": float(avg_loss),

            "expectancy": float(expectancy),
        })

    # Debug logs (safe to keep during dev)
    print("STRATEGY RAW ROWS:", rows)
    print("STRATEGY FINAL:", result)

    return result