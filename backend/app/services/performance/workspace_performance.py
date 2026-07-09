from __future__ import annotations

"""
Trading Truth Layer
Workspace Performance Builder

Projects aggregated workspace analytics into the
canonical WorkspacePerformanceMetrics contract.

This module performs:

    • NO database access

    • NO SQL

    • NO analytics calculations

It only transforms an already-computed
workspace analytics payload into the
institutional performance model.
"""

from app.services.performance.performance_models import (
    WorkspacePerformanceMetrics,
)


# ============================================================
# WORKSPACE PERFORMANCE BUILDER
# ============================================================

def build_workspace_performance_metrics(
    *,
    workspace_id: int,
    analytics: dict,
) -> WorkspacePerformanceMetrics:
    """
    Builds the canonical performance metrics
    for an entire workspace.

    The analytics payload must already have
    been computed by the canonical analytics
    layer.

    This function performs no calculations.
    """

    analytics = analytics or {}

    return WorkspacePerformanceMetrics(

        workspace_id=workspace_id,

        claim_count=int(
            analytics.get(
                "claim_count",
                0,
            )
        ),

        trade_count=int(
            analytics.get(
                "trade_count",
                0,
            )
        ),

        net_profit=float(
            analytics.get(
                "net_profit",
                analytics.get(
                    "net_pnl",
                    0,
                ),
            )
        ),

        gross_profit=float(
            analytics.get(
                "gross_profit",
                0,
            )
        ),

        gross_loss=float(
            analytics.get(
                "gross_loss",
                0,
            )
        ),

        profit_factor=float(
            analytics.get(
                "profit_factor",
                0,
            )
        ),

        expectancy=float(
            analytics.get(
                "expectancy",
                0,
            )
        ),

        average_win=float(
            analytics.get(
                "average_win",
                0,
            )
        ),

        average_loss=float(
            analytics.get(
                "average_loss",
                0,
            )
        ),

        payoff_ratio=float(
            analytics.get(
                "payoff_ratio",
                0,
            )
        ),

        win_rate=float(
            analytics.get(
                "win_rate",
                0,
            )
        ),

        loss_rate=float(
            analytics.get(
                "loss_rate",
                0,
            )
        ),

        winning_trades=int(
            analytics.get(
                "winning_trades",
                0,
            )
        ),

        losing_trades=int(
            analytics.get(
                "losing_trades",
                0,
            )
        ),

        max_drawdown=float(
            analytics.get(
                "max_drawdown",
                0,
            )
        ),

        recovery_factor=float(
            analytics.get(
                "recovery_factor",
                0,
            )
        ),

        performance_band=analytics.get(
            "performance_band",
            "Unclassified",
        ),

        metadata={

            "performance_version": "1.0",

            "analytics_engine": "Trading Performance System",

        },

    )