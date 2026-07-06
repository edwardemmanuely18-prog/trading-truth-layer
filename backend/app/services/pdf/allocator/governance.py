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

def _band(component):

    if component is None:
        return "-"

    value = getattr(
        component,
        "band",
        None,
    )

    if value is None:
        value = getattr(
            component,
            "status",
            None,
        )

    if value is None:
        return "-"

    return str(value).replace(
        "_",
        " ",
    ).title()


def _score(component):

    if component is None:
        return "-"

    value = getattr(
        component,
        "earned_points",
        None,
    )

    if value is None:
        value = getattr(
            component,
            "score",
            None,
        )

    if value is None:
        return "-"

    return f"{float(value):.2f}%"


# ==========================================================
# GOVERNANCE
# ==========================================================

def build_governance_section(report):
    """
    Institutional Governance Assessment.

    Consumes the canonical TVS
    Verification Certificate.

    No governance calculations are
    performed here.
    """

    workspace = report["workspace_verification"]

    story = []

    #
    # Narrative
    #

    story.extend(

        build_section(

            "Operational Governance",

            build_narrative(

                """
                Governance evaluates the operational
                controls surrounding a verified trading
                record.

                Rather than measuring profitability,
                governance measures auditability,
                evidence custody, operational integrity
                and lifecycle protection throughout the
                Trading Verification System.
                """

            ),

        )

    )

    #
    # Governance Summary
    #

    rows = [

        [
            "Governance Metric",
            "Assessment",
        ],

        [
            "Governance",
            f"{workspace.governance.percentage:.2f}%",
        ],

        [
            "Integrity",
            f"{workspace.integrity.percentage:.2f}%",
        ],

        [
            "Transparency",
            f"{workspace.transparency.percentage:.2f}%",
        ],

        [
            "Average Verification Score",
            f"{workspace.average_verification_score:.2f}%",
        ],

        [
            "Verified Claims",
            workspace.claim_count,
        ],

        [
            "Verified Trades",
            report["performance"]["trade_count"],
        ],

        [
            "Evidence Aggregation",
            "TVS Derived",
        ],

        [
            "Allocator Scope",
            "Workspace",
        ],

        [
            "Network",
            f"{workspace.network.percentage:.2f}%",
        ],

        [
            "Reviews",
            f"{workspace.reviews.percentage:.2f}%",
        ],

        [
            "Disputes",
            f"{workspace.disputes.percentage:.2f}%",
        ],

        [
            "Stability",
            f"{workspace.stability.percentage:.2f}%",
        ],

    ]

    story.extend(

        build_metric_block(

            "Governance Controls",

            build_metric_table(

                rows,

            ),

        )

    )

    #
    # Governance Interpretation
    #

    story.extend(

        build_callout(

            "Institutional Interpretation",

            (
                "Governance maturity reflects the "
                "strength of operational controls "
                "surrounding the trading record. "
                "Institutional allocators typically "
                "require strong governance before "
                "capital allocation decisions are "
                "made. Governance within Trading "
                "Truth Layer is evaluated directly "
                "by the Trading Verification System "
                "and incorporated into the "
                "Verification Certificate."
            ),

        )

    )

    return story