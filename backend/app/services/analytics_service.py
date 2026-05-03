from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.trade import Trade


def get_strategy_performance(db: Session, workspace_id: int):
    # ✅ SIMPLE + CORRECT: use strategy_tag directly (no joins)
    rows = (
        db.query(
            Trade.strategy_tag.label("tag"),
            func.count(Trade.id).label("trade_count"),
            func.coalesce(func.sum(Trade.net_pnl), 0).label("net_pnl"),
            func.coalesce(func.avg(Trade.net_pnl), 0).label("avg_pnl"),
            func.sum(case((Trade.net_pnl > 0, 1), else_=0)).label("wins"),
            func.sum(case((Trade.net_pnl <= 0, 1), else_=0)).label("losses"),
        )
        # DEBUG MODE
        # .filter(Trade.workspace_id == workspace_id)
        .group_by(Trade.strategy_tag)
        .all()
    )

    result = []

    for r in rows:
        total = int(r.trade_count or 0)
        wins = int(r.wins or 0)
        losses = int(r.losses or 0)

        net_pnl = float(r.net_pnl or 0)

        # ✅ safe calculations
        win_rate = (wins / total) if total > 0 else 0.0

        # ⚠️ simplified (we’ll upgrade later)
        avg_win = (net_pnl / wins) if wins > 0 else 0.0
        avg_loss = (net_pnl / losses) if losses > 0 else 0.0

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

    print("STRATEGY DEBUG:", result)    

    return result