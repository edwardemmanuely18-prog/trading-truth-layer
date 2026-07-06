from __future__ import annotations

from app.services.pdf.common.institutional_sections import (
    build_section,
    build_metric_block,
    build_callout,
    build_narrative,
    build_recommendations,
)

from app.services.pdf.common.institutional_tables import (
    build_metric_table,
)

from app.services.pdf.common.institutional_theme import (
    VERDICT_STYLE,
)

from reportlab.platypus import Paragraph

from reportlab.platypus import KeepTogether

from app.services.pdf.common.institutional_utils import short_hash

# ==========================================================
# FINAL VERDICT
# ==========================================================

def build_verdict_section(
    report,
    report_hash=None,
    verification_url=None,
):
    """
    Final Institutional Verdict.

    This is the executive decision page of the
    allocator report.

    It performs no calculations and simply
    summarizes the conclusions reached by
    previous analytical sections.
    """

    allocator = report["allocator_assessment"]

    workspace = report["workspace_verification"]

    story = []

    #
    # Executive Heading
    #

    story.extend(
        build_section(

            "Institutional Allocation Verdict",

            build_narrative(

                """
                The Trading Truth Layer Allocator
                Report concludes with an institutional
                assessment derived from trading
                analytics together with the Trading
                Verification System (TVS).

                This verdict summarizes the overall
                suitability of the verified trading
                record for institutional capital
                allocation review.
                """

            ),

        )

    )

    #
    # Verdict Banner
    #

    story.append(

        Paragraph(

            allocator.get(
                "allocator_band",
                "Further Review Required",
            ),

            VERDICT_STYLE,

        )

    )

    dashboard = [

        ["Decision", allocator["verdict"]],

        ["Allocator Grade", allocator["allocator_band"]],

        [
            "Institutional Ready",
            "YES"
            if allocator["allocator_score"] >= 85
            else "NO",
        ],

        [
            "Review Required",
            "YES"
            if allocator["allocator_score"] < 85
            else "NO",
        ],

    ]

    story.extend(

        build_metric_block(

            "Institutional Decision",

            build_metric_table(

                dashboard,

            ),

        )

    )

    #
    # Executive Summary Table
    #

    rows = [

        [
            "Institutional Metric",
            "Result",
        ],

        [
            "Allocator Score",
            allocator.get(
                "allocator_score",
                "-",
            ),
        ],

        [
            "Average Verification Score",
            f"{workspace.average_verification_score:.2f}%",
        ],

        [
            "Verification Band",
            workspace.verification_band,
        ],

        [
            "Verified Claims",
            workspace.claim_count,
        ],

    ]

    story.extend(

        build_metric_block(

            "Executive Decision Summary",

            build_metric_table(

                rows,

            ),

        )

    )

    #
    # Decision Commentary
    #

    story.extend(

        build_callout(

            "Institutional Commentary",

            (
                "The allocator recommendation "
                "reflects a combined assessment of "
                "historical trading performance, "
                "downside risk, governance maturity "
                "and the independently generated "
                "Trading Verification Certificate. "
                "No single metric should be used in "
                "isolation when evaluating capital "
                "allocation suitability."
            ),

        )

    )

    #
    # Guidance
    #

    score = allocator.get(
        "allocator_score",
        0,
    )

    if score >= 85:

        guidance = [

            "Suitable for institutional capital review.",

            "Continue periodic TVS verification.",

            "Maintain governance and evidence controls.",

            "Preserve immutable evidence lineage.",

        ]

    elif score >= 70:

        guidance = [

            "Further verification history is recommended.",

            "Increase governance maturity.",

            "Strengthen verification coverage.",

            "Repeat allocator assessment after additional verified trading activity.",

        ]

    else:

        guidance = [

            "Institutional allocation is not currently recommended.",

            "Address operational observations identified in this report.",

            "Improve verification quality before reassessment.",

            "Generate a new TVS certificate after corrective actions.",

        ]

    story.extend(
        build_recommendations(

            guidance,

        )

    )

    #
    # Report Identity
    #

    identity_rows = [

        [
            "Verification Scope",
            "Workspace",
        ],

        [
            "Verification Engine",
            "Trading Verification System (TVS)",
        ],

        [
            "Verified Claims",
            workspace.claim_count,
        ],

        [
            "Aggregation",
            workspace.metadata.get(
                "aggregation",
                "-",
            ),
        ],

        [
            "Verification Endpoint",
            verification_url or "-",
        ],

        [
            "Report Hash",
            short_hash(report_hash, 24),
        ],

    ]

    story.extend(

        build_metric_block(

            "Verification Identity",

            build_metric_table(

                identity_rows,

            ),

        )

    )

    #
    # Closing Statement
    #

    story.extend(

        build_callout(

            "Closing Statement",

            (
                "This report represents the "
                "institutional opinion of the "
                "Trading Truth Layer Verification "
                "System at the time of issuance. "
                "Future trading activity, evidence "
                "updates or governance changes may "
                "result in a different Verification "
                "Certificate and allocator outcome."
            ),

        )

    )

    story.extend(

        build_callout(

            "End of Verified Report",

            (
                "This document was generated by the "
                "Trading Truth Layer Trading Verification "
                "System (TVS).\n\n"
                f"Verification URL:\n{verification_url}"
            ),

        )

    )

    return story