from __future__ import annotations

from app.services.analytics.workspace_analytics_models import (
    WorkspaceClaimAnalytics,
    WorkspaceMetricsAnalytics,
)


def build_workspace_metrics_analytics(
    *,
    claim_metrics: list[
        WorkspaceClaimAnalytics
    ],
):

    if not claim_metrics:

        return WorkspaceMetricsAnalytics(

            metrics={

                "claim_count": 0,

                "trade_count": 0,

                "net_profit": 0.0,

                "gross_profit": 0.0,

                "gross_loss": 0.0,

                "profit_factor": 0.0,

                "expectancy": 0.0,

                "average_win": 0.0,

                "average_loss": 0.0,

                "payoff_ratio": 0.0,

                "winning_trades": 0,

                "losing_trades": 0,

                "win_rate": 0.0,

                "loss_rate": 0.0,

                "max_drawdown": 0.0,

                "recovery_factor": 0.0,

                "performance_band": "No Data",

            }

        )

    total_claims = len(
        claim_metrics
    )

    total_trades = 0

    total_wins = 0

    total_losses = 0

    gross_profit = 0.0

    gross_loss = 0.0

    net_profit = 0.0

    max_drawdown = 0.0

    expectancy = 0.0

    average_win = 0.0

    average_loss = 0.0

    payoff_ratio = 0.0

    recovery_factor = 0.0

    for claim in claim_metrics:

        metrics = claim.metrics

        total_trades += metrics[
            "trade_count"
        ]

        total_wins += metrics[
            "winning_trades"
        ]

        total_losses += metrics[
            "losing_trades"
        ]

        gross_profit += metrics[
            "gross_profit"
        ]

        gross_loss += metrics[
            "gross_loss"
        ]

        net_profit += metrics[
            "net_profit"
        ]

        max_drawdown = max(

            max_drawdown,

            metrics[
                "max_drawdown"
            ],

        )

    total_closed_trades = (

        total_wins
        +
        total_losses

    )

    if gross_loss > 0:

        profit_factor = round(

            gross_profit
            /
            gross_loss,

            4,

        )

    else:

        profit_factor = round(
            gross_profit,
            4,
        )

    if total_closed_trades:

        win_rate = round(

            (
                total_wins
                /
                total_closed_trades
            )
            * 100,

            4,

        )

        loss_rate = round(

            (
                total_losses
                /
                total_closed_trades
            )
            * 100,

            4,

        )

    else:

        win_rate = 0.0

        loss_rate = 0.0

    if total_trades:

        expectancy = round(

            net_profit
            /
            total_trades,

            4,

        )

    if total_wins:

        average_win = round(

            gross_profit
            /
            total_wins,

            4,

        )

    if total_losses:

        average_loss = round(

            gross_loss
            /
            total_losses,

            4,

        )

    if average_loss > 0:

        payoff_ratio = round(

            average_win
            /
            average_loss,

            4,

        )

    if max_drawdown > 0:

        recovery_factor = round(

            net_profit
            /
            max_drawdown,

            4,

        )

    if profit_factor >= 2:

        performance_band = "STRONG"

    elif profit_factor >= 1.2:

        performance_band = "MODERATE"

    else:

        performance_band = "WEAK"

    return WorkspaceMetricsAnalytics(

        metrics={

            "claim_count":
                total_claims,

            "trade_count":
                total_trades,

            "net_profit":
                round(
                    net_profit,
                    4,
                ),

            "gross_profit":
                round(
                    gross_profit,
                    4,
                ),

            "gross_loss":
                round(
                    gross_loss,
                    4,
                ),

            "profit_factor":
                profit_factor,

            "expectancy":
                expectancy,

            "average_win":
                average_win,

            "average_loss":
                average_loss,

            "payoff_ratio":
                payoff_ratio,

            "winning_trades":
                total_wins,

            "losing_trades":
                total_losses,

            "win_rate":
                win_rate,

            "loss_rate":
                loss_rate,

            "max_drawdown":
                round(
                    max_drawdown,
                    4,
                ),

            "recovery_factor":
                recovery_factor,

            "performance_band":
                performance_band,

        }

    )