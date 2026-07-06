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
# INTERNAL
# ==========================================================

def _component_band(component):

    if component is None:
        return "-"

    band = getattr(
        component,
        "band",
        None,
    )

    if not band:
        return "-"

    return str(band).replace(
        "_",
        " ",
    ).title()


def _component_score(component):

    if component is None:
        return "-"

    score = getattr(
        component,
        "earned_points",
        None,
    )

    if score is None:
        score = getattr(
            component,
            "score",
            None,
        )

    if score is None:
        return "-"

    return f"{float(score):.2f}%"


# ==========================================================
# TVS VERIFICATION
# ==========================================================

def build_verification_section(report):
    """
    Trading Verification System (TVS).

    This section consumes the canonical
    Verification Certificate.

    No verification mathematics are
    performed here.
    """

    workspace = report["workspace_verification"]

    certificates = report.get(
        "workspace_certificates",
        [],
    )

    scores = sorted(
        c.summary.verification_score
        for c in certificates
    )

    highest = max(scores) if scores else 0
    lowest = min(scores) if scores else 0

    average = (
        sum(scores) / len(scores)
        if scores
        else 0
    )

    median = (
        scores[len(scores)//2]
        if scores
        else 0
    )

    story = []

    #
    # Narrative
    #

    story.extend(

        build_section(

            "Trading Verification System (TVS)",

            build_narrative(

                """
                The Trading Verification System
                independently evaluates the
                credibility of reported trading
                activity.

                Verification is independent from
                profitability and measures
                evidence authenticity,
                governance maturity,
                operational integrity,
                transparency and provenance.
                """

            ),

        )

    )

    #
    # Executive Verification
    #

    executive = [

        ["Verification Metric", "Workspace"],

        [
            "Average Verification Score",
            f"{average:.2f}%",
        ],

        [
            "Highest Certificate",
            f"{highest:.2f}%",
        ],

        [
            "Lowest Certificate",
            f"{lowest:.2f}%",
        ],

        [
            "Median Certificate",
            f"{median:.2f}%",
        ],

        [
            "Verification Band",
            workspace.verification_band,
        ],

        [
            "Verified Claims",
            workspace.claim_count,
        ],

        [
            "Verified Trades",
            report["performance"]["trade_count"],
        ],

    ]

    story.extend(

        build_metric_block(

            "Verification Summary",

            build_metric_table(

                executive,

            ),

        )

    )

    #
    # Portfolio Verification Distribution
    #

    rows = [

        [
            "Portfolio Verification",
            "Value",
        ],

        [
            "Verified Claims",
            len(certificates),
        ],

        [
            "Verified Trades",
            report["performance"]["trade_count"],
        ],

        [
            "Average Score",
            f"{average:.2f}%",
        ],

        [
            "Highest Claim",
            f"{highest:.2f}%",
        ],

        [
            "Lowest Claim",
            f"{lowest:.2f}%",
        ],

        [
            "Median Score",
            f"{median:.2f}%",
        ],

    ]

    story.extend(

        build_metric_block(

            "Portfolio Verification Distribution",

            build_metric_table(

                rows,

            ),

        )

    )

    #
    # Interpretation
    #

    story.extend(

        build_callout(

            "Institutional Interpretation",

            (
                "The Verification Certificate is the "
                "single source of truth for all "
                "verification surfaces within "
                "Trading Truth Layer. Every "
                "verification score presented in "
                "this report originates directly "
                "from the Trading Verification "
                "System (TVS)."
            ),

        )

    )

    return story