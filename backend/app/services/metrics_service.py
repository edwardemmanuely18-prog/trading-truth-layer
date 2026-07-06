from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.workspace import Workspace

from app.services.entitlements import (
    resolve_workspace_plan_code,
    get_workspace_plan_limits,
)
from app.services.trade_metrics_service import (
    compute_trade_metrics,
    build_equity_curve,
    compute_drawdown_stats,
)


def get_workspace_trade_metrics(
    db: Session,
    workspace_id: int,
) -> dict:

    trades = db.query(Trade).filter(
        Trade.workspace_id == workspace_id
    ).all()

    metrics = compute_trade_metrics(
        trades
    )

    equity_curve = build_equity_curve(
        trades
    )

    drawdown = compute_drawdown_stats(
        equity_curve["curve"]
    )

    total = len(trades)

    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id
    ).first()

    limits = get_workspace_plan_limits(
        workspace
    )

    limit = limits["trades"]

    wins = 0
    losses = 0
    total_pnl = 0

    for trade in trades:
        pnl = trade.net_pnl or 0

        total_pnl += pnl

        if pnl > 0:
            wins += 1

        elif pnl < 0:
            losses += 1

    decisive_trades = (
        wins + losses
    )

    win_rate = (
        (wins / decisive_trades) * 100
        if decisive_trades > 0
        else 0
    )

    """
    IMPORTANT:

    Governed trade usage is immutable.

    Imports increase governed usage.
    Deleting trades MUST NOT reduce it.

    Therefore:
    - used = lifetime consumed imports
    - ledger_count = current DB rows
    """

    used = (
        getattr(
            workspace,
            "trades_consumed_count",
            0,
        )
        or 0
    )

    utilization = (
        (used / limit) * 100
        if limit > 0
        else 0
    )

    effective_plan_code = (
        resolve_workspace_plan_code(
            workspace
        )
    )

    return {
        # IMMUTABLE GOVERNANCE
        "used": used,
        "consumed": used,

        # LIVE LEDGER
        "ledger_count": total,

        # PLAN GOVERNANCE
        "limit": limit,

        "effective_plan_code": (
            effective_plan_code
        ),

        "configured_plan_code": (
            getattr(
                workspace,
                "plan_code",
                "sandbox",
            )
            if workspace
            else "sandbox"
        ),

        # UTILIZATION
        "utilization": round(
            utilization,
            2,
        ),

        # ANALYTICS
        "win_rate": round(
            win_rate,
            2,
        ),

        "total_pnl": round(
            total_pnl,
            2,
        ),

        "wins": wins,
        "losses": losses,

        "trade_count": metrics["trade_count"],

        "profit_factor":
            metrics["profit_factor"],

        "gross_profit":
            metrics["gross_profit"],

        "gross_loss":
            metrics["gross_loss"],

        "average_win":
            metrics["average_win"],

        "average_loss":
            metrics["average_loss"],

        "payoff_ratio":
            metrics["payoff_ratio"],

        "expectancy":
            round(
                metrics["net_pnl"]
                / metrics["trade_count"],
                2,
            )
            if metrics["trade_count"]
            else 0,

        # DRAWDOWN

        "max_drawdown":
            round(
                drawdown.get(
                    "max_drawdown",
                    0,
                ),
                2,
            ),

        "peak_to_trough_drawdown_units":
            round(
                drawdown.get(
                    "max_drawdown",
                    0,
                ),
                2,
            ),

        "drawdown_peak":
            drawdown.get(
                "peak_cumulative",
                0,
            ),

        "drawdown_trough":
            drawdown.get(
                "trough_cumulative",
                0,
            ),

        "has_drawdown":
            drawdown.get(
                "has_drawdown",
                False,
            ),

        "decisive_trades": decisive_trades,
        
        "scratch_trades": total - decisive_trades,
            }