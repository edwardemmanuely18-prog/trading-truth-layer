from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.trade import Trade
from app.models.trade_tag import TradeTag
from app.models.trade_tag_map import TradeTagMap


def get_strategy_performance(db: Session, workspace_id: int):

    rows = (
        db.query(
            TradeTag.name.label("tag"),
            func.count(Trade.id).label("trade_count"),
            func.coalesce(func.sum(Trade.net_pnl), 0).label("net_pnl"),
            func.coalesce(func.avg(Trade.net_pnl), 0).label("avg_pnl"),
            func.sum(
                case((Trade.net_pnl > 0, 1), else_=0)
            ).label("wins"),
            func.sum(
                case((Trade.net_pnl <= 0, 1), else_=0)
            ).label("losses"),
        )
        .join(TradeTagMap, TradeTag.id == TradeTagMap.tag_id)
        .join(Trade, Trade.id == TradeTagMap.trade_id)
        .filter(Trade.workspace_id == workspace_id)
        .group_by(TradeTag.name)
        .all()
    )

    result = []

    for r in rows:
        total = r.trade_count or 0
        wins = r.wins or 0
        losses = r.losses or 0

        win_rate = (wins / total) if total > 0 else 0

        avg_win = (r.net_pnl / wins) if wins > 0 else 0
        avg_loss = (r.net_pnl / losses) if losses > 0 else 0

        expectancy = (
            (win_rate * avg_win) - ((1 - win_rate) * abs(avg_loss))
            if total > 0 else 0
        )

        result.append({
            "tag": r.tag,
            "trade_count": int(total),
            "net_pnl": float(r.net_pnl or 0),
            "avg_pnl": float(r.avg_pnl or 0),
            "win_rate": float(win_rate),
            "avg_win": float(avg_win),
            "avg_loss": float(avg_loss),
            "expectancy": float(expectancy),
        })

    return result