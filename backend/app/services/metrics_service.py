from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.workspace import Workspace


def normalize_plan_code(plan_code: str | None) -> str:
    allowed = {
        "sandbox",
        "starter",
        "pro",
        "growth",
        "business",
    }

    normalized = str(
        plan_code or "sandbox"
    ).strip().lower()

    if normalized not in allowed:
        return "sandbox"

    return normalized


def normalize_billing_status(
    billing_status: str | None,
) -> str:
    allowed = {
        "inactive",
        "active",
        "trialing",
        "past_due",
        "canceled",
        "unpaid",
    }

    normalized = str(
        billing_status or "inactive"
    ).strip().lower()

    if normalized not in allowed:
        return "inactive"

    return normalized


def is_paid_billing_status(
    billing_status: str | None,
) -> bool:
    normalized = normalize_billing_status(
        billing_status
    )

    return normalized in {
        "active",
        "trialing",
    }


def resolve_effective_plan_code(
    workspace: Workspace | None,
) -> str:
    """
    Canonical governance resolution.

    IMPORTANT:
    Paid plans ONLY become effective when billing
    is active or trialing.

    Otherwise workspace falls back into sandbox
    governance.
    """

    if not workspace:
        return "sandbox"

    configured_plan = normalize_plan_code(
        getattr(workspace, "plan_code", "sandbox")
    )

    billing_status = normalize_billing_status(
        getattr(workspace, "billing_status", "inactive")
    )

    # sandbox and starter are always allowed
    if configured_plan in {
        "sandbox",
        "starter",
    }:
        return configured_plan

    # paid governance only activates
    # when billing active
    if is_paid_billing_status(
        billing_status
    ):
        return configured_plan

    # inactive paid workspaces fallback
    # into sandbox governance
    return "sandbox"


def get_workspace_plan_snapshot(
    effective_plan_code: str,
) -> dict:
    """
    SINGLE SOURCE OF TRUTH
    for governance limits.
    """

    PLAN_LIMITS = {
        "sandbox": {
            "member_limit": 3,
            "trade_limit": 200,
            "claim_limit": 2,
            "storage_limit_mb": 100,
        },

        "starter": {
            "member_limit": 3,
            "trade_limit": 5000,
            "claim_limit": 5,
            "storage_limit_mb": 500,
        },

        "pro": {
            "member_limit": 25,
            "trade_limit": 50000,
            "claim_limit": 50,
            "storage_limit_mb": 2048,
        },

        "growth": {
            "member_limit": 100,
            "trade_limit": 250000,
            "claim_limit": 200,
            "storage_limit_mb": 10240,
        },

        "business": {
            "member_limit": 250,
            "trade_limit": 1000000,
            "claim_limit": 500,
            "storage_limit_mb": 51200,
        },
    }

    return PLAN_LIMITS.get(
        effective_plan_code,
        PLAN_LIMITS["sandbox"],
    )


def resolve_workspace_trade_limit(
    workspace: Workspace | None,
) -> int:
    """
    Centralized trade-limit resolution.

    NO router imports.
    NO circular imports.
    FULL governance consistency.
    """

    effective_plan_code = (
        resolve_effective_plan_code(
            workspace
        )
    )

    snapshot = get_workspace_plan_snapshot(
        effective_plan_code
    )

    return int(
        snapshot.get("trade_limit") or 200
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

    limit = resolve_workspace_trade_limit(
        workspace
    )

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
        resolve_effective_plan_code(
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
        "effective_plan_code": effective_plan_code,
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
    }

