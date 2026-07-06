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

def _pretty_band(value):

    if value is None:
        return "-"

    value = str(value).replace("_", " ")

    if value.lower().startswith("tier "):
        return value.title()

    if value.lower() == "tier 1":
        return "Tier I"

    if value.lower() == "tier 2":
        return "Tier II"

    if value.lower() == "tier 3":
        return "Tier III"

    return value.title()


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def build_executive_summary(report):
    """
    Institutional executive summary.

    This module owns only the executive
    content.

    Layout, spacing, typography and
    presentation are delegated to the
    institutional framework.
    """

    allocator = report["allocator_assessment"]

    performance = report["performance"]

    risk = report["risk"]

    verification = report["verification"]

    evidence = report["evidence"]

    integrity = report["integrity"]

    governance = report["governance"]

    trust = report["trust"]

    story = []

    #
    # Executive Narrative
    #

    narrative = build_narrative(

        """
        This report presents an institutional
        due diligence assessment of historical
        trading performance, operational risk,
        verification confidence, governance
        maturity and evidence quality.

        The objective is to provide institutional
        allocators with a concise investment
        assessment before reviewing the detailed
        analytical sections.
        """

    )

    story.extend(

        build_section(

            "Executive Summary",

            narrative,

        )

    )

    #
    # Allocator Assessment
    #

    allocator_rows = [

        ["Assessment", "Result"],

        [

            "Allocator Score",

            allocator["allocator_score"],

        ],

        [

            "Allocator Band",

            allocator["allocator_band"],

        ],

        [

            "Capital Allocation",

            allocator["allocation_capacity"],

        ],

    ]

    story.extend(

        build_metric_block(

            "Allocator Assessment",

            build_metric_table(

                allocator_rows,

            ),

        )

    )

    highlights = [

        ["Executive Highlight", "Value"],

        [
            "Trades",
            performance["trade_count"],
        ],

        [
            "Net Profit",
            performance["net_profit"],
        ],

        [
            "Profit Factor",
            performance["profit_factor"],
        ],

        [
            "Verification Score",
            verification["verification_score"],
        ],

        [
            "Allocator Score",
            allocator["allocator_score"],
        ],

        [
            "Verdict",
            allocator["verdict"],
        ],

    ]

    story.extend(

        build_metric_block(

            "Executive Highlights",

            build_metric_table(

                highlights,

            ),

        )

    )

    #
    # Trading Assessment
    #

    trading_rows = [

        ["Assessment", "Result"],

        [

            "Performance",

            performance["performance_band"],

        ],

        [

            "Risk",

            risk["risk_band"],

        ],

    ]

    story.extend(

        build_metric_block(

            "Trading Assessment",

            build_metric_table(

                trading_rows,

            ),

        )

    )

    #
    # TVS Assessment
    #

    verification_rows = [

        ["Component", "Result"],

        [

            "Verification",

            verification["verification_band"],

        ],

        [

            "Evidence",

            _pretty_band(

                evidence["quality_band"],

            ),

        ],

        [

            "Integrity",

            integrity["integrity_band"],

        ],

        [

            "Governance",

            governance["governance_band"],

        ],

        [

            "Trust",

            trust["trust_band"],

        ],

    ]

    story.extend(

        build_metric_block(

            "TVS Assessment",

            build_metric_table(

                verification_rows,

            ),

        )

    )

    #
    # Executive Interpretation
    #

    story.extend(

        build_callout(

            "Executive Interpretation",

            (
                "Trading Truth Layer combines "
                "trading analytics with institutional "
                "verification through the Trading "
                "Verification System (TVS). "
                "The allocator assessment should be "
                "considered alongside the detailed "
                "performance, verification, governance "
                "and risk analyses that follow."
            ),

        )

    )

    return story