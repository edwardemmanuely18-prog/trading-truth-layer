from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
)

from app.services.trade_metrics_service import (
    compute_trade_metrics,
)

from app.services.performance.builders.member_builder import (
    build_member_performance_metrics,
)


def get_workspace_member_performance(
    db: Session,
    workspace_id: int,
):
    """
    Canonical TPS workspace member
    performance aggregation.

    This replaces the legacy
    build_leaderboard() implementation.
    """

    schemas = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .all()
    )

    members = defaultdict(
        lambda: {
            "member_id": "",
            "member_name": "",
            "workspace_id": workspace_id,
            "claim_count": 0,
            "trade_count": 0,
            "net_profit": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "winning_trades": 0,
            "losing_trades": 0,
        }
    )

    for schema in schemas:

        trades = resolve_schema_trades(
            schema,
            db,
        )

        grouped = defaultdict(list)

        for trade in trades:

            member = (
                trade.member_id
                or "Unknown"
            )

            grouped[member].append(
                trade
            )

        for member, member_trades in grouped.items():

            metrics = compute_trade_metrics(
                member_trades
            )

            row = members[member]

            row["member_id"] = member
            row["member_name"] = member

            row["claim_count"] += 1

            row["trade_count"] += metrics["trade_count"]

            row["net_profit"] += metrics["net_pnl"]

            row["gross_profit"] += metrics["gross_profit"]

            row["gross_loss"] += metrics["gross_loss"]

            row["winning_trades"] += metrics["winning_trades"]

            row["losing_trades"] += metrics["losing_trades"]

    results = []

    for row in members.values():

        gross_loss = abs(
            row["gross_loss"]
        )

        profit_factor = (
            row["gross_profit"] / gross_loss
            if gross_loss
            else row["gross_profit"]
        )

        total_closed = (
            row["winning_trades"] +
            row["losing_trades"]
        )

        win_rate = (
            row["winning_trades"] /
            total_closed
            if total_closed
            else 0
        )

        results.append(

            build_member_performance_metrics(

                member_id=row["member_id"],

                member_name=row["member_name"],

                workspace_id=workspace_id,

                claim_count=row["claim_count"],

                trade_count=row["trade_count"],

                net_profit=row["net_profit"],

                gross_profit=row["gross_profit"],

                gross_loss=row["gross_loss"],

                profit_factor=profit_factor,

                expectancy=0,

                average_win=0,

                average_loss=0,

                payoff_ratio=0,

                winning_trades=row["winning_trades"],

                losing_trades=row["losing_trades"],

                win_rate=win_rate,

                loss_rate=1 - win_rate,

                max_drawdown=0,

                recovery_factor=0,

                performance_band="Workspace Member",

            )

        )

    results.sort(

        key=lambda x: x.net_profit,

        reverse=True,

    )

    return results