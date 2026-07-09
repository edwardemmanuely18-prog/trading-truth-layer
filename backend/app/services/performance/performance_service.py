from __future__ import annotations

"""
Trading Truth Layer
Trading Performance System (TPS)

Canonical public entry point for trading
performance throughout Trading Truth Layer.

This service is the ONLY entry point that
should be consumed by:

    • Claim Report PDF

    • Allocator Report PDF

    • Dashboard

    • Public Claim

    • Workspace APIs

    • Claim APIs

No consumer should compute trading metrics
directly.

No consumer should assemble performance
objects manually.
"""

from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
)

from app.services.trade_metrics_service import (
    compute_trade_metrics,
)

from app.services.performance.claim_performance import (
    build_claim_performance_metrics,
)

from app.services.performance.workspace_performance import (
    build_workspace_performance_metrics,
)


# ============================================================
# INTERNAL ANALYTICS ENTRY POINT
# ============================================================

def _build_claim_analytics(
    db: Session,
    claim: ClaimSchema,
) -> dict:
    """
    Internal analytics adapter.

    Temporary implementation.

    During migration this function adapts the
    existing analytics layer into the canonical
    TPS contract.

    Eventually this will call the institutional
    analytics engine directly.
    """

    #
    # --------------------------------------------------------
    # TODO
    #
    # Replace with canonical analytics engine.
    #
    # For now we return an empty payload so
    # downstream contracts remain stable.
    #
    # --------------------------------------------------------
    #

    trades = resolve_schema_trades(
        claim,
        db,
    )

    return compute_trade_metrics(
        trades,
    )


# ============================================================
# CLAIM PERFORMANCE
# ============================================================

def get_claim_performance_metrics(
    db: Session,
    claim: ClaimSchema,
):
    """
    Canonical single-claim performance.

    Every single-claim consumer inside TTL
    should call this function.

    No consumer should compute trading metrics
    independently.
    """

    analytics = _build_claim_analytics(
        db=db,
        claim=claim,
    )

    return build_claim_performance_metrics(

        claim_schema_id=claim.id,

        workspace_id=claim.workspace_id,

        analytics=analytics,

    )


# ============================================================
# WORKSPACE PERFORMANCE
# ============================================================

def get_workspace_performance_metrics(
    db: Session,
    workspace_id: int,
):
    """
    Canonical workspace performance.

    This aggregates workspace analytics into
    the canonical WorkspacePerformanceMetrics
    contract.
    """

    #
    # --------------------------------------------------------
    # TODO
    #
    # Replace with canonical workspace analytics.
    #
    # --------------------------------------------------------
    #

    from app.models.claim_schema import ClaimSchema

    schemas = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .all()
    )

    claim_metrics = []

    total_trades = 0

    total_wins = 0

    total_losses = 0

    gross_profit = 0.0

    gross_loss = 0.0

    net_profit = 0.0

    max_drawdown = 0.0

    for claim in schemas:

        analytics = _build_claim_analytics(
            db=db,
            claim=claim,
        )

        if analytics.get("trade_count", 0):

            claim_metrics.append(
                analytics
            )

            total_trades += analytics["trade_count"]

            total_wins += analytics["winning_trades"]

            total_losses += analytics["losing_trades"]

            gross_profit += analytics["gross_profit"]

            gross_loss += analytics["gross_loss"]

            net_profit += analytics["net_profit"]

            max_drawdown = max(
                max_drawdown,
                analytics["max_drawdown"],
            )

    if not claim_metrics:

        analytics = {}

    else:

        if gross_loss > 0:

            workspace_pf = gross_profit / gross_loss

        else:

            workspace_pf = gross_profit

        if workspace_pf >= 2:

            performance_band = "STRONG"

        elif workspace_pf >= 1.2:

            performance_band = "MODERATE"

        else:

            performance_band = "WEAK"

        analytics = {

            "claim_count": len(claim_metrics),

            "trade_count": sum(
                m["trade_count"]
                for m in claim_metrics
            ),

            "winning_trades": sum(
                m["winning_trades"]
                for m in claim_metrics
            ),

            "losing_trades": sum(
                m["losing_trades"]
                for m in claim_metrics
            ),

            "net_profit": sum(
                m["net_profit"]
                for m in claim_metrics
            ),

            "gross_profit": sum(
                m["gross_profit"]
                for m in claim_metrics
            ),

            "gross_loss": sum(
                m["gross_loss"]
                for m in claim_metrics
            ),

            "profit_factor": (
                round(
                    gross_profit / gross_loss,
                    4,
                )
                if gross_loss > 0
                else round(
                    gross_profit,
                    4,
                )
            ),

            "expectancy": (
                round(
                    net_profit / total_trades,
                    4,
                )
                if total_trades
                else 0
            ),

            "average_win": (
                round(
                    gross_profit / total_wins,
                    4,
                )
                if total_wins
                else 0
            ),

            "average_loss": (
                round(
                    gross_loss / total_losses,
                    4,
                )
                if total_losses
                else 0
            ),

            "payoff_ratio": (
                round(
                    (gross_profit / total_wins)
                    /
                    (gross_loss / total_losses),
                    4,
                )
                if total_wins
                and total_losses
                and gross_loss > 0
                else 0
            ),

            "win_rate": (
                round(
                    total_wins
                    /
                    (total_wins + total_losses)
                    * 100,
                    4,
                )
                if (total_wins + total_losses)
                else 0
            ),

            "loss_rate": (
                round(
                    total_losses
                    /
                    (total_wins + total_losses)
                    * 100,
                    4,
                )
                if (total_wins + total_losses)
                else 0
            ),

            "max_drawdown":
                max_drawdown,

            "recovery_factor": (
                round(
                    net_profit / max_drawdown,
                    4,
                )
                if max_drawdown > 0
                else 0
            ),

            "performance_band":
                performance_band,

        }

    return build_workspace_performance_metrics(
        workspace_id=workspace_id,
        analytics=analytics,
    )