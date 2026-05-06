from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.workspace import Workspace


def resolve_workspace_trade_limit(workspace: Workspace | None) -> int:
    """
    Centralized trade-limit resolution without importing billing routes.
    Avoids circular imports between services and API routers.
    """

    if not workspace:
        return 200

    plan_code = str(
        getattr(workspace, "plan_code", "sandbox") or "sandbox"
    ).strip().lower()

    billing_status = str(
        getattr(workspace, "billing_status", "inactive") or "inactive"
    ).strip().lower()

    # GOVERNED PLAN LIMITS
    PLAN_LIMITS = {
        "sandbox": 200,
        "starter": 5000,
        "pro": 50000,
        "growth": 250000,
        "enterprise": 1000000,
    }

    # If billing inactive, keep workspace in sandbox governance
    effective_plan = (
        plan_code
        if billing_status == "active"
        else "sandbox"
    )

    return int(
        PLAN_LIMITS.get(
            effective_plan,
            200,
        )
    )


def get_workspace_trade_metrics(
    db: Session,
    workspace_id: int,
) -> dict:

    trades = db.query(Trade).filter(
        Trade.workspace_id == workspace_id
    ).all()

    total = len(trades)

    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id
    ).first()

    limit = resolve_workspace_trade_limit(workspace)

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

    win_rate = (
        (wins / total) * 100
        if total > 0
        else 0
    )

    # BILLING / GOVERNANCE CONSUMPTION
    used = (
        getattr(workspace, "trades_consumed_count", None)
        or total
    )

    utilization = (
        (used / limit) * 100
        if limit > 0
        else 0
    )

    return {
        "used": used,
        "consumed": used,

        # REAL DB RECORDS
        "ledger_count": total,

        # GOVERNANCE
        "limit": limit,
        "utilization": round(utilization, 2),

        # ANALYTICS
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "wins": wins,
        "losses": losses,
    }