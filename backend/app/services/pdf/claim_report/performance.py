from __future__ import annotations

"""
Trading Truth Layer
Claim Report

Trading Performance

This section presents the verified trading
performance associated with a single claim.

All analytics are consumed from the
canonical TVS payload.

No calculations occur here.
"""

from app.services.pdf.common.institutional_sections import (
    build_section,
    build_metric_block,
    build_callout,
    build_narrative,
    build_findings,
)

from app.services.pdf.common.institutional_tables import (
    build_metric_table,
)



# ==========================================================
# PRESENTATION HELPERS
# ==========================================================

def metric(value, decimals=2):

    if value is None:
        return "Not Available"

    try:
        return f"{float(value):,.{decimals}f}"
    except Exception:
        return str(value)


def percentage(value):

    if value is None:
        return "Not Available"

    try:
        value = float(value)

        if value <= 1:
            value *= 100

        return f"{value:.1f}%"

    except Exception:
        return str(value)


def integer(value):

    if value is None:
        return "Not Available"

    return f"{int(value):,}"


# ==========================================================
# PERFORMANCE
# ==========================================================

def build_performance_section(
    context: dict,
):

    performance = context["performance"]

    summary = performance["summary"]

    risk = performance["risk"]

    assessment = performance["assessment"]

    story = []

    #
    # Executive Narrative
    #

    story.extend(

        build_section(

            "Trading Performance Assessment",

            build_narrative(

                """
                This section presents the historical
                trading performance associated with the
                submitted claim.

                Performance analytics are provided by
                the canonical Trading Performance
                System (TPS), which evaluates trading
                outcomes, consistency, profitability
                and risk characteristics independently
                from institutional verification,
                evidence provenance and governance
                assessment performed by the Trading
                Verification System (TVS).
                """

            ),

        )

    )

    #
    # ------------------------------------------------------
    # Performance Overview
    # ------------------------------------------------------
    #

    overview_rows = [

        ["Trading Metric", "Result"],

        ["Performance Band",
         assessment.get("performance_band", "Not Available")],

        ["Net Profit",
         metric(summary.get("net_profit"))],

        ["Gross Profit",
         metric(summary.get("gross_profit"))],

        ["Gross Loss",
         metric(summary.get("gross_loss"))],

        ["Total Trades",
         integer(summary.get("trade_count"))],

        ["Winning Trades",
         integer(summary.get("winning_trades"))],

        ["Losing Trades",
         integer(summary.get("losing_trades"))],

    ]

    story.extend(

        build_metric_block(

            "Trading Performance Profile",

            build_metric_table(
                overview_rows,
            ),

        )

    )

    #
    # ------------------------------------------------------
    # Risk Analytics
    # ------------------------------------------------------
    #

    risk_rows = [

        ["Risk Metric", "Result"],

        ["Profit Factor",
         metric(risk.get("profit_factor"))],

        ["Maximum Drawdown",
         metric(risk.get("max_drawdown"))],

        ["Recovery Factor",
         metric(risk.get("recovery_factor"))],

        ["Expectancy",
         metric(risk.get("expectancy"))],

        ["Payoff Ratio",
         metric(risk.get("payoff_ratio"))],

    ]

    story.extend(

        build_metric_block(

            "Risk & Return Characteristics",

            build_metric_table(
                risk_rows,
            ),

        )

    )

    #
    # ------------------------------------------------------
    # Consistency Metrics
    # ------------------------------------------------------
    #

    consistency_rows = [

        ["Consistency Metric", "Result"],

        ["Win Rate",
         percentage(summary.get("win_rate"))],

        ["Loss Rate",
         percentage(summary.get("loss_rate"))],

        ["Average Winning Trade",
         metric(risk.get("average_win"))],

        ["Average Losing Trade",
         metric(risk.get("average_loss"))],

        ["Best Trade",
         metric(summary.get("best_trade"))],

        ["Worst Trade",
         metric(summary.get("worst_trade"))],

    ]

    story.extend(

        build_metric_block(

            "Trading Consistency",

            build_metric_table(
                consistency_rows,
            ),

        )

    )

    story.extend(

        build_findings(

            [

                (
                    f"The submitted trading record contains "
                    f"{integer(summary.get('trade_count'))} verified trades "
                    f"and is classified as "
                    f"{assessment.get('performance_band', 'Not Available')}."
                ),

                (
                    f"Historical Profit Factor is "
                    f"{metric(risk.get('profit_factor'))}."
                ),

                (
                    f"Maximum realized drawdown is "
                    f"{metric(risk.get('max_drawdown'))}."
                ),

            ],

            title="Key Performance Findings",

        )

    )

    return story