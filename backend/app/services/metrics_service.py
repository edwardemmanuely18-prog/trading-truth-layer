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

    win_rate = (
        (wins / total) * 100
        if total > 0
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

        "expectancy":
            round(
                (
                    metrics["net_pnl"]
                    / metrics["trade_count"]
                )
                if metrics["trade_count"]
                else 0,
                2,
            ),

        "max_drawdown":
            drawdown["max_drawdown"],
            }