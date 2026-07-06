from __future__ import annotations

from app.services.pdf.common.institutional_sections import (
    build_section,
    build_metric_block,
    build_callout,
    build_narrative,
)

from app.services.pdf.common.institutional_tables import (
    build_metric_table,
)


# ==========================================================
# PERFORMANCE SECTION
# ==========================================================

def build_performance_section(report):
    """
    Institutional Trading Performance Assessment.

    This module owns only trading analytics.

    Presentation, spacing and typography are
    delegated to the institutional framework.
    """

    performance = report["performance"]

    risk = report["risk"]

    story = []

    #
    # Section Narrative
    #

    story.extend(

        build_section(

            "Trading Performance Assessment",

            build_narrative(

                """
                Historical trading performance is evaluated
                independently from verification quality.

                This section measures profitability,
                expectancy, consistency and downside
                control using standardized institutional
                trading metrics.

                Trading analytics describe how the
                strategy has historically performed,
                while TVS evaluates the integrity and
                verifiability of those results.
                """

            ),

        )

    )

    #
    # Performance Metrics
    #

    metrics = [

        ["Trading Metric", "Result"],

        [
            "Total Trades",
            performance.get(
                "trade_count",
                "-",
            ),
        ],

        [
            "Net Profit",
            performance.get(
                "net_profit",
                "-",
            ),
        ],

        [
            "Gross Profit",
            performance.get(
                "gross_profit",
                "-",
            ),
        ],

        [
            "Gross Loss",
            performance.get(
                "gross_loss",
                "-",
            ),
        ],

        [
            "Profit Factor",
            performance.get(
                "profit_factor",
                "-",
            ),
        ],

        [
            "Win Rate",
            performance.get(
                "win_rate",
                "-",
            ),
        ],

        [
            "Loss Rate",
            performance.get(
                "loss_rate",
                "-",
            ),
        ],

        [
            "Expectancy",
            performance.get(
                "expectancy",
                "-",
            ),
        ],

        [
            "Average Win",
            performance.get(
                "average_win",
                "-",
            ),
        ],

        [
            "Average Loss",
            performance.get(
                "average_loss",
                "-",
            ),
        ],

        [
            "Payoff Ratio",
            performance.get(
                "payoff_ratio",
                "-",
            ),
        ],

        [
            "Maximum Drawdown",
            risk.get(
                "max_drawdown",
                "-",
            ),
        ],

        [
            "Recovery Factor",
            risk.get(
                "recovery_factor",
                "-",
            ),
        ],

        [
            "Performance Band",
            performance.get(
                "performance_band",
                "-",
            ),
        ],

    ]

    story.extend(

        build_metric_block(

            "Performance Metrics",

            build_metric_table(

                metrics,

            ),

        )

    )

    #
    # Institutional Interpretation
    #

    observations = []

    if performance["performance_band"] == "STRONG":
        observations.append(
            "Historical profitability exceeded institutional thresholds."
        )

    if float(str(risk["recovery_factor"]).replace("%","").replace("$","")) >= 1:
        observations.append(
            "Recovery characteristics remained favourable."
        )

    if observations:

        story.extend(

            build_callout(

                "Performance Observations",

                "\n".join(observations),

            )

        )

    story.extend(

        build_callout(

            "Institutional Interpretation",

            (
                "Institutional allocators evaluate "
                "historical profitability together "
                "with downside control. Strong "
                "returns supported by controlled "
                "drawdowns, positive expectancy and "
                "consistent payoff characteristics "
                "generally indicate greater capital "
                "allocation suitability than raw "
                "profitability alone."
            ),

        )

    )

    return story