from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.trade import Trade


def get_strategy_performance(
    db: Session,
    workspace_id: int,
    strategy: str | None = None,
):
    """
    Institutional-grade strategy analytics.

    Uses canonical Trade.strategy_tag field.
    """

    strategy_expr = func.coalesce(
        Trade.strategy_tag,
        "unclassified",
    )

    query = (
        db.query(
            strategy_expr.label("tag"),

            func.count(Trade.id).label("trade_count"),

            func.coalesce(
                func.sum(Trade.net_pnl),
                0,
            ).label("net_pnl"),

            func.coalesce(
                func.avg(Trade.net_pnl),
                0,
            ).label("avg_pnl"),

            func.sum(
                case((Trade.net_pnl > 0, 1), else_=0)
            ).label("wins"),

            func.sum(
                case((Trade.net_pnl <= 0, 1), else_=0)
            ).label("losses"),

            func.coalesce(
                func.sum(
                    case(
                        (Trade.net_pnl > 0, Trade.net_pnl),
                        else_=0,
                    )
                ),
                0,
            ).label("win_pnl"),

            func.coalesce(
                func.sum(
                    case(
                        (Trade.net_pnl < 0, Trade.net_pnl),
                        else_=0,
                    )
                ),
                0,
            ).label("loss_pnl"),
        )
        .filter(Trade.workspace_id == workspace_id)
    )

    # -------------------------
    # STRATEGY FILTER
    # -------------------------
    if strategy and strategy != "All":
        query = query.filter(
            strategy_expr == strategy
        )

    rows = (
        query
        .group_by(strategy_expr)
        .order_by(func.sum(Trade.net_pnl).desc())
        .all()
    )

    result = []

    for r in rows:
        total = int(r.trade_count or 0)

        wins = int(r.wins or 0)
        losses = int(r.losses or 0)

        net_pnl = float(r.net_pnl or 0)
        avg_pnl = float(r.avg_pnl or 0)

        win_pnl = float(r.win_pnl or 0)
        loss_pnl = float(r.loss_pnl or 0)

        win_rate = (
            wins / total
            if total > 0 else 0.0
        )

        avg_win = (
            win_pnl / wins
            if wins > 0 else 0.0
        )

        avg_loss = (
            loss_pnl / losses
            if losses > 0 else 0.0
        )

        expectancy = (
            (win_rate * avg_win)
            - ((1 - win_rate) * abs(avg_loss))
            if total > 0 else 0.0
        )

        result.append({
            "tag": r.tag or "unclassified",

            "trade_count": total,

            "net_pnl": round(net_pnl, 2),

            "avg_pnl": round(avg_pnl, 2),

            "win_rate": round(win_rate, 4),

            "avg_win": round(avg_win, 2),

            "avg_loss": round(avg_loss, 2),

            "expectancy": round(expectancy, 2),
        })

    print("STRATEGY PERFORMANCE FINAL:", result)

    return result