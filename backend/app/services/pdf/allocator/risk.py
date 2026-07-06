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
# RISK ASSESSMENT
# ==========================================================

def build_risk_section(report):
    """
    Institutional Risk Assessment.

    This section evaluates historical downside
    characteristics of the trading record.

    Risk analytics are intentionally independent
    from TVS verification.
    """

    risk = report["risk"]

    performance = report["performance"]

    story = []

    #
    # Narrative
    #

    story.extend(

        build_section(

            "Risk Assessment",

            build_narrative(

                """
                Institutional allocators evaluate
                downside protection before expected
                return.

                This section summarizes historical
                drawdown behaviour, capital
                preservation characteristics and
                overall risk profile independently
                from verification quality.
                """

            ),

        )

    )

    #
    # Risk Metrics
    #

    rows = [

        [
            "Risk Metric",
            "Result",
        ],

        [
            "Risk Band",
            risk.get(
                "risk_band",
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
            "Risk / Reward",
            risk.get(
                "payoff_ratio",
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

            "Risk Metrics",

            build_metric_table(

                rows,

            ),

        )

    )

    #
    # Institutional Interpretation
    #

    story.extend(

        build_callout(

            "Institutional Interpretation",

            (
                "Institutional capital allocation "
                "prioritizes capital preservation "
                "before return generation. "
                "Strategies exhibiting controlled "
                "drawdowns together with stable "
                "profitability are generally viewed "
                "as more resilient over extended "
                "investment horizons."
            ),

        )

    )

    return story