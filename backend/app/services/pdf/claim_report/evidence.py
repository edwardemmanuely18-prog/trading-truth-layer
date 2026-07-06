from __future__ import annotations

"""
Trading Truth Layer
Claim Report

Evidence Assessment

Institutional assessment of the evidence
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


# ==========================================================
# TIER FORMATTER
# ==========================================================

def tier(value):

    if not value:
        return "Not Available"

    mapping = {
        "tier_1": "Tier I",
        "tier_2": "Tier II",
        "tier_3": "Tier III",
        "TIER_1": "Tier I",
        "TIER_2": "Tier II",
        "TIER_3": "Tier III",
    }

    return mapping.get(str(value), str(value))


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
# EVIDENCE
# ==========================================================

def build_evidence_section(
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

            "Evidence Assessment",

            build_narrative(

                """
                Institutional due diligence begins with
                the quality, provenance and traceability
                of the evidence supporting a submitted
                trading claim.

                The Trading Verification System (TVS)
                assesses evidence authenticity,
                completeness and source reliability
                before performing institutional
                verification.

                Evidence quality is evaluated
                independently from historical trading
                performance and provides the foundation
                upon which subsequent verification,
                governance and audit conclusions are
                established.
                """

            ),

        )

    )

    #
    # Evidence Dashboard
    #

    rows = [

        [
            "Evidence Metric",
            "Result",
        ],

        [
            "Evidence Status",
            display_status(
                verification.evidence.status,
            ),
        ],

        [
            "Evidence Score",
            score(
                verification.evidence,
            ),
        ],

        [
            "Primary Evidence Tier",
            tier(verification.primary_tier),
        ],

        [
            "Primary Evidence Source",
            str(
                verification.primary_source,
            ).replace("_", " ").title(),
        ],

        [
            "Tier I Coverage",
            f'{verification.tier1_count} ({verification.tier1_percent:.1f}%)',
        ],

        [
            "Tier II Coverage",
            f'{verification.tier2_count} ({verification.tier2_percent:.1f}%)',
        ],

        [
            "Tier III Coverage",
            f'{verification.tier3_count} ({verification.tier3_percent:.1f}%)',
        ],

    ]

    story.extend(

        build_metric_block(

            "Evidence Quality Profile",

            build_metric_table(
                rows,
            ),

        )

    )

    #
    # Institutional Evidence Profile
    #

    tier_profile = {

        "primary_tier":
            getattr(
                verification,
                "primary_tier",
                "Unknown",
            ),

        "primary_source":
            getattr(
                verification,
                "primary_source",
                "Unknown",
            ),

        "tier1_count":
            getattr(
                verification,
                "tier1_count",
                0,
            ),

        "tier2_count":
            getattr(
                verification,
                "tier2_count",
                0,
            ),

        "tier3_count":
            getattr(
                verification,
                "tier3_count",
                0,
            ),

        "tier1_percent":
            getattr(
                verification,
                "tier1_percent",
                0.0,
            ),

        "tier2_percent":
            getattr(
                verification,
                "tier2_percent",
                0.0,
            ),

        "tier3_percent":
            getattr(
                verification,
                "tier3_percent",
                0.0,
            ),

    }

    #
    # Evidence Analysis
    #

    analysis_rows = [

        [
            "Evidence Domain",
            "Institutional Assessment",
        ],

        [
            "Evidence Quality",
            verification.evidence.reason,
        ],

        [
            "Integrity",
            verification.integrity.reason,
        ],

        [
            "Transparency",
            verification.transparency.reason,
        ],

        [
            "Network Validation",
            verification.network.reason,
        ],

    ]

    story.extend(

        build_metric_block(

            "Institutional Evidence Assessment",

            build_metric_table(
                analysis_rows,
            ),

        )

    )

    #
    # Evidence Component Scores
    #

    component_rows = [

        [
            "Evidence Component",
            "Score",
            "Assessment",
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
            "Transparency",
            score(
                verification.transparency,
            ),
            display_status(
                verification.transparency.status,
            ),
        ],

        [
            "Network",
            score(
                verification.network,
            ),
            display_status(
                verification.network.status,
            ),
        ],

    ]

    story.extend(

        build_metric_block(

            "Evidence Control Matrix",

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
    # Evidence Recommendations
    #

    recommendations = []

    for component in [

        verification.evidence,
        verification.integrity,
        verification.transparency,
        verification.network,

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

                title="Due Diligence Recommendations",

            )

        )

    story.extend(

        build_findings(

            [

                f"The submitted claim is primarily supported by {tier(verification.primary_tier)} evidence.",

                f"Evidence provenance demonstrates {display_status(verification.evidence.status)} institutional quality.",

                "Integrity and transparency controls support independent institutional review of the submitted trading record.",

                "Evidence provenance should be considered alongside verification, governance and audit findings when evaluating institutional reliability.",

            ],

            title="Key Evidence Findings",

        )

    )

    return story