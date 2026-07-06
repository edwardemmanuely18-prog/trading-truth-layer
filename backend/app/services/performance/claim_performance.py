from __future__ import annotations

"""
Trading Truth Layer
Claim Performance Builder

Projects canonical trade analytics into the
ClaimPerformanceMetrics contract.

This module performs:

    • NO database access

    • NO SQL

    • NO verification

    • NO analytics calculations

It only transforms an already-computed
analytics payload into the canonical
institutional performance model.
"""

from app.services.performance.performance_models import (
    ClaimPerformanceMetrics,
)


# ============================================================
# CLAIM PERFORMANCE BUILDER
# ============================================================

def build_claim_performance_metrics(
    *,
    claim_schema_id: int,
    workspace_id: int,
    analytics: dict,
) -> ClaimPerformanceMetrics:
    """
    Builds the canonical performance model for
    a single verified claim.

    Parameters
    ----------
    analytics

        Canonical analytics payload produced
        by the institutional analytics layer.

    This builder never computes metrics.
    """

    analytics = analytics or {}

    return ClaimPerformanceMetrics(

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        claim_schema_id=claim_schema_id,

        workspace_id=workspace_id,

        trade_count=int(
            analytics.get(
                "trade_count",
                0,
            )
        ),

        # --------------------------------------------------
        # Profitability
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Win / Loss
        # --------------------------------------------------

        winning_trades=int(
            analytics.get(
                "winning_trades",
                analytics.get(
                    "wins",
                    0,
                ),
            )
        ),

        losing_trades=int(
            analytics.get(
                "losing_trades",
                analytics.get(
                    "losses",
                    0,
                ),
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

        # --------------------------------------------------
        # Risk
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        performance_band=analytics.get(
            "performance_band",
            "Unclassified",
        ),

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        metadata={

            "performance_version": "1.0",

            "analytics_engine": "Trading Performance System",

        },

    )