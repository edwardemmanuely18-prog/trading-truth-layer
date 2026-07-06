from __future__ import annotations

"""
Trading Truth Layer
Claim Report

Operational Governance

Institutional assessment of the governance,
transparency and operational controls
supporting a verified trading claim.

Consumes only the canonical
ClaimVerificationMetrics object.

No verification logic exists here.
"""

from app.services.pdf.common.institutional_sections import (
    build_section,
    build_metric_block,
    build_callout,
    build_narrative,
    build_findings,
    build_recommendations,
)

from app.services.pdf.common.institutional_tables import (
    build_metric_table,
)

from app.services.pdf.common.institutional_theme import (
    CONTENT_WIDTH,
)


# ==========================================================
# PRESENTATION HELPERS
# ==========================================================

def score(component):

    return (
        f"{component.earned_points} / "
        f"{component.maximum_points}"
    )


def display_status(value):

    if not value:
        return "Not Available"

    mapping = {
        "tier_1": "Tier I",
        "tier_2": "Tier II",
        "tier_3": "Tier III",
        "locked": "Locked",
        "valid": "Valid",
        "transparent": "Transparent",
    }

    return mapping.get(
        str(value).lower(),
        str(value).replace("_", " ").title(),
    )


# ==========================================================
# GOVERNANCE
# ==========================================================

def build_governance_section(
    context: dict,
):

    verification = context["verification"]

    certificate = context["certificate"]

    story = []

    #
    # Narrative
    #

    story.extend(

        build_section(

            "Operational Governance",

            build_narrative(

                """
                Institutional governance evaluates the
                operational framework supporting a
                verified trading claim.

                Beyond historical trading performance,
                institutional participants assess the
                governance, transparency, integrity and
                control environment surrounding reported
                results.

                The Trading Verification System (TVS)
                evaluates these governance characteristics
                independently from trading performance and
                uses them to determine the operational
                credibility of the submitted claim.
                """

            ),

        )

    )

    #
    # Governance Dashboard
    #

    rows = [

        [
            "Governance Metric",
            "Result",
        ],

        [
            "Governance Status",
            display_status(
                verification.governance.status,
            ),
        ],

        [
            "Governance Score",
            score(
                verification.governance,
            ),
        ],

        [
            "Transparency Status",
            display_status(
                verification.transparency.status,
            ),
        ],

        [
            "Integrity Status",
            display_status(
                verification.integrity.status,
            ),
        ],

        [
            "Evidence Control",
            display_status(
                verification.evidence.status,
            ),
        ],

    ]

    story.extend(

        build_metric_block(

            "Governance Dashboard",

            build_metric_table(
                rows,
            ),

        )

    )

    #
    # Governance Analysis
    #

    analysis_rows = [

        [
            "Governance Domain",
            "Institutional Assessment",
        ],

        [
            "Governance",
            verification.governance.reason,
        ],

        [
            "Transparency",
            verification.transparency.reason,
        ],

        [
            "Integrity",
            verification.integrity.reason,
        ],

        [
            "Evidence Controls",
            verification.evidence.reason,
        ],

    ]

    story.extend(

        build_metric_block(

            "Governance Control Assessment",

            build_metric_table(
                analysis_rows,
            ),

        )

    )

    #
    # Governance Component Scores
    #

    component_rows = [

        [
            "Governance Component",
            "Score",
            "Assessment",
        ],

        [
            "Governance",
            score(
                verification.governance,
            ),
            display_status(
                verification.governance.status,
            ),
        ],

        [
            "Transparency",
            score(
                verification.transparency,
            ),
            display_status(
                verification.transparency.status,
            ),
        ],

        [
            "Integrity",
            score(
                verification.integrity,
            ),
            display_status(
                verification.integrity.status,
            ),
        ],

        [
            "Evidence",
            score(
                verification.evidence,
            ),
            display_status(
                verification.evidence.status,
            ),
        ],

    ]

    story.extend(

        build_metric_block(

            "Governance Control Matrix",

            build_metric_table(
                component_rows,
                col_widths=[
                    CONTENT_WIDTH * 0.42,
                    CONTENT_WIDTH * 0.20,
                    CONTENT_WIDTH * 0.38,
                ],
            ),

        )

    )

    #
    # Governance Recommendations
    #

    recommendations = []

    for component in [

        verification.governance,
        verification.transparency,
        verification.integrity,
        verification.evidence,

    ]:

        recommendations.extend(

            getattr(

                component,

                "recommendations",

                [],

            )

        )

    if recommendations:

        story.extend(

            build_recommendations(

                recommendations,

                title="Governance Improvement Recommendations",

            )

        )

    story.extend(

        build_findings(

            [

                f"Operational governance demonstrates {verification.governance.status.lower()} institutional maturity.",

                "Transparency controls support independent institutional review.",

                "Integrity controls strengthen the credibility of the submitted trading claim.",

                "Governance quality should be considered together with evidence, verification and audit findings during institutional due diligence.",

            ],

            title="Key Governance Findings",

        )

    )

    return story