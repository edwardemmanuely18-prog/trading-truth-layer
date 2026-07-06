from __future__ import annotations

"""
Trading Truth Layer
Claim Report

Verification Assessment

Institutional presentation of the
canonical Trading Verification System
(TVS) assessment.

Consumes only the canonical
ClaimVerificationMetrics object.
"""

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


def confidence(value):

    if value is None:
        return "Not Available"

    value = float(value)

    if value <= 1:
        value *= 100

    return f"{value:.1f}%"


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
# VERIFICATION
# ==========================================================

def build_verification_section(
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

            "Trading Verification Assessment",

            build_narrative(

                """
                This section presents the institutional
                Trading Verification System (TVS)
                assessment supporting the submitted
                trading claim.

                Verification evaluates evidence quality,
                governance maturity, transparency,
                operational integrity and network
                validation independently from historical
                trading performance.
                """

            ),

        )

    )

    #
    # Verification Certificate
    #

    certificate_rows = [

        [
            "Verification Metric",
            "Result",
        ],

        [
            "Verification Status",
            display_status(
                verification.verification_status,
            ),
        ],

        [
            "Verification Tier",
            tier(verification.verification_tier),
        ],

        [
            "Verification Band",
            verification.verification_band,
        ],

        [
            "Overall Verification Score",
            f"{verification.verification_score:.1f}",
        ],

        [
            "Institutional Decision",
            verification.decision,
        ],

        [
            "Institutional Confidence",
            confidence(
                verification.confidence,
            ),
        ],

    ]

    story.extend(

        build_metric_block(

            "Verification Certificate",

            build_metric_table(
                certificate_rows,
            ),

        )

    )

    #
    # TVS Component Matrix
    #

    component_rows = [

        [
            "Core Component",
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

    ]

    story.extend(

        build_metric_block(

            "Core TVS Assessment",

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

    supporting_rows = [

        [
            "Supporting Component",
            "Score",
            "Maximum",
            "Status",
        ],

        [
            "Stability",
            verification.stability.earned_points,
            verification.stability.maximum_points,
            display_status(
                verification.stability.status,
            ),
        ],

        [
            "Network",
            verification.network.earned_points,
            verification.network.maximum_points,
            display_status(
                verification.network.status,
            ),
        ],

        [
            "Reviews",
            verification.reviews.earned_points,
            verification.reviews.maximum_points,
            display_status(
                verification.reviews.status,
            ),
        ],

        [
            "Disputes",
            verification.disputes.earned_points,
            verification.disputes.maximum_points,
            display_status(
                verification.disputes.status,
            ),
        ],

    ]

    story.extend(

        build_metric_block(

            "Supporting TVS Assessment",

            build_metric_table(
                supporting_rows,
                col_widths=[
                    CONTENT_WIDTH * 0.35,
                    CONTENT_WIDTH * 0.15,
                    CONTENT_WIDTH * 0.15,
                    CONTENT_WIDTH * 0.35,
                ],
            ),

        )

    )

    #
    # Decision
    #

    decision_rows = [

        [
            "Decision Property",
            "Value",
        ],

        [
            "Institutional Decision",
            verification.decision,
        ],

        [
            "Verification Confidence",
            confidence(
                verification.confidence,
            ),
        ],

        [
            "Verification Status",
            display_status(
                verification.verification_status,
            ),
        ],

    ]

    story.extend(

        build_metric_block(

            "Verification Decision",

            build_metric_table(
                decision_rows,
            ),

        )

    )

    #
    # Verification Warnings
    #

    if verification.warnings:

        warning_rows = [

            [
                "Verification Exceptions",
            ],

        ]

        for warning in verification.warnings:

            warning_rows.append(

                [
                    warning,
                ]

            )

        story.extend(

            build_metric_block(

                "Verification Warnings",

                build_metric_table(
                    warning_rows,
                ),

            )

        )

    #
    # Institutional Recommendations
    #

    if verification.recommendations:

        story.extend(

            build_recommendations(

                verification.recommendations,

                title="Verification Recommendations",

            )

        )

    #
    # Institutional Interpretation
    #

    story.extend(

        build_callout(

            "Institutional Interpretation",

            (
                "The Verification Certificate represents "
                "the canonical institutional opinion "
                "generated by the Trading Verification "
                "System. Individual component assessments "
                "are aggregated into a unified verification "
                "decision that reflects the confidence "
                "institutional participants may place in "
                "the submitted trading claim."
            ),

        )

    )

    return story