from __future__ import annotations

from collections import defaultdict

from app.services.trade_metrics_service import (
    compute_trade_metrics,
)

from app.services.analytics.workspace_analytics_models import (
    WorkspaceClaimAnalytics,
    WorkspaceMemberAnalytics,
)


def build_workspace_member_analytics(
    *,
    claim_metrics: list[
        WorkspaceClaimAnalytics
    ],
):

    members = defaultdict(
        list,
    )

    #
    # Aggregate trades by member.
    #

    for claim in claim_metrics:

        for trade in claim.trades:

            member_id = (
                trade.member_id
                or "Unknown"
            )

            members[
                member_id
            ].append(
                trade
            )

    results = []

    #
    # Compute member metrics only once.
    #

    for member_id, trades in members.items():

        metrics = compute_trade_metrics(
            trades,
        )

        results.append(

            WorkspaceMemberAnalytics(

                metrics={

                    "member_id":
                        member_id,

                    "claim_count":
                        len(

                            {

                                c.claim.id

                                for c in claim_metrics

                                if any(

                                    t.member_id
                                    == member_id

                                    for t in c.trades

                                )

                            }

                        ),

                    "trade_count":
                        metrics[
                            "trade_count"
                        ],

                    "net_profit":
                        metrics[
                            "net_profit"
                        ],

                    "gross_profit":
                        metrics[
                            "gross_profit"
                        ],

                    "gross_loss":
                        metrics[
                            "gross_loss"
                        ],

                    "profit_factor":
                        metrics[
                            "profit_factor"
                        ],

                    "win_rate":
                        metrics[
                            "win_rate"
                        ],

                    "max_drawdown":
                        metrics[
                            "max_drawdown"
                        ],

                    "performance_band":
                        metrics[
                            "performance_band"
                        ],

                },

            )

        )

    return sorted(

        results,

        key=lambda x:
        x.metrics[
            "net_profit"
        ],

        reverse=True,

    )