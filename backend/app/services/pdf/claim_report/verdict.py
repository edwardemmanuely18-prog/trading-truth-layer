from __future__ import annotations

"""
Trading Truth Layer
Claim Report

Institutional Verification Verdict

Final institutional opinion for a verified
trading claim.

Consumes only the canonical Claim Report
context.

No verification logic exists here.
"""

from app.services.pdf.common.institutional_sections import (
    build_section,
    build_metric_block,
    build_callout,
    build_recommendations,
    build_narrative,
)

from app.services.pdf.common.institutional_tables import (
    build_metric_table,
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


def display_status(value):

    if not value:
        return "Not Available"

    mapping = {
        "locked": "Locked",
        "valid": "Valid",
        "transparent": "Transparent",
        "tier_1": "Tier I",
        "tier_2": "Tier II",
        "tier_3": "Tier III",
    }

    return mapping.get(
        str(value).lower(),
        str(value).replace("_"," ").title(),
    )


# ==========================================================
# FINAL VERDICT
# ==========================================================

def build_verdict_section(
    context: dict,
    report_hash: str | None = None,
    verification_url: str | None = None,
):

    verification = context["verification"]

    certificate = context["certificate"]

    metadata = context["metadata"]

    performance = context["performance"]

    story = []

    #
    # Narrative
    #

    story.extend(

        build_section(

            "Institutional Verification Verdict",

            build_narrative(

                """
                This chapter presents the consolidated
                institutional opinion derived from the
                preceding performance, evidence,
                verification, governance and audit
                assessments.

                Rather than introducing new information,
                the Institutional Verdict synthesizes the
                findings of the Trading Performance
                System (TPS) and the Trading Verification
                System (TVS) into a final due diligence
                conclusion suitable for allocators,
                auditors and institutional reviewers.
                """

            ),

        )

    )

    #
    # Executive Verdict
    #

    rows = [

        [
            "Institutional Decision",
            "Result",
        ],

        [
            "Verification Decision",
            verification.decision,
        ],

        [
            "Verification Status",
            display_status(
                verification.verification_status,
            ),
        ],

        [
            "Verification Band",
            verification.verification_band,
        ],

        [
            "Institutional Confidence",
            confidence(
                verification.confidence,
            ),
        ],

        [
            "Trading Performance",
            performance["assessment"].get(
                "performance_band",
                "-",
            ),
        ],

        [
            "Historical Trades",
            performance["summary"].get(
                "trade_count",
                "-",
            ),
        ],

    ]

    story.extend(

        build_metric_block(

            "Institutional Verdict",

            build_metric_table(
                rows,
            ),

        )

    )

    #
    # Recommendations
    #

    story.extend(

        build_recommendations(
            verification.recommendations,
        )

    )

    #
    # Warnings
    #

    if verification.warnings:

        warning_rows = [

            [
                "Warning",
            ],

        ]

        for warning in verification.warnings:

            warning_rows.append(
                [warning]
            )

        story.extend(

            build_metric_block(

                "Residual Risk Factors",

                build_metric_table(
                    warning_rows,
                ),

            )

        )

    if verification_url:

        if verification_url.startswith("/"):

            verification_url = (
                "https://www.tradingtruthlayer.com"
                + verification_url
            )

        story.extend(

            build_section(

                "Independent Verification Reference",

                build_narrative(

                    [

                        (
                            "<b>Verification Portal</b>"
                        ),

                        verification_url,

                        (
                            "<b>Certificate Hash</b>"
                        ),

                        certificate.identity.certificate_hash,

                        (
                            "Scan the QR code provided in this report "
                            "to independently verify this Verification "
                            "Certificate through the official "
                            "Trading Truth Layer verification portal."
                        ),

                    ]

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
                "The institutional opinion presented in this report "
                "is derived from the combined assessments of the "
                "Trading Performance System (TPS) and the Trading "
                "Verification System (TVS). Together these canonical "
                "systems evaluate historical trading performance, "
                "evidence quality, governance maturity, operational "
                "integrity and auditability to produce a transparent, "
                "reproducible and institutionally defensible due "
                "diligence assessment."
            ),

        )

    )

    story.extend(

        build_callout(

            "Institutional Verification Complete",

            (

                "This institutional assessment has been completed "
                "using the canonical Trading Performance System (TPS) "
                "and Trading Verification System (TVS).\n\n"

                "The verification opinion presented throughout this "
                "report reflects the evidence, governance, audit and "
                "performance information available at the time of "
                "assessment.\n\n"

                "The accompanying Verification Portal and QR code "
                "allow independent validation of this certificate "
                "through the official Trading Truth Layer platform."

            ),

        )

    )

    return story