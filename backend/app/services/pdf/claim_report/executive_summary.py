from __future__ import annotations

"""
Trading Truth Layer
Claim Report

Executive Summary

Institutional executive overview for a
single verified claim.

Consumes only the canonical Claim Report
context.

No business logic is performed here.
"""

from app.services.pdf.common.institutional_sections import (
    build_section,
    build_metric_block,
    build_callout,
    build_narrative,
    build_findings,
)

from app.services.pdf.common.institutional_tables import (
    build_metric_table,
)

from app.services.verification.intelligence.verification_tiers import (
    get_tier,
)


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

def build_executive_summary(
    context: dict,
):

    verification = context["verification"]

    performance = context["performance"]

    summary = performance["summary"]

    risk = performance["risk"]

    assessment = performance["assessment"]

    evidence = context["evidence"]

    tier_profile = evidence["tier_profile"]

    verification_tier = get_tier(
        verification.verification_tier
    ).label

    evidence_tier = get_tier(
        tier_profile["primary_tier"]
    ).label

    story = []

    #
    # Narrative
    #

    story.extend(

        build_section(

            "Executive Summary",

            build_narrative(

                """

                This Institutional Claim Report documents the
                independent assessment of a single verified
                trading claim submitted to Trading Truth Layer.

                The report combines the analytical conclusions
                of the Trading Performance System (TPS) with
                the governance, evidence, transparency,
                operational integrity and verification
                assessments produced by the Trading Verification
                System (TVS).

                Together these independent institutional
                assessment engines establish whether the
                submitted trading record is both historically
                representative and institutionally credible.

                The following sections progressively evaluate
                trading performance, evidence provenance,
                verification quality, governance maturity,
                audit lineage and the final institutional
                opinion supporting this claim.

                """

            ),

        )

    )

    story.extend(

        build_findings(

            [

                f"Verification Decision: {verification.decision}",

                f"Verification Score: {verification.verification_score:.1f}/100",

                f"Verification Band: {verification.verification_band}",

                f"Verification Tier: {verification_tier}",

                f"Historical Trades Reviewed: {summary['trade_count']}",

                f"Evidence Tier: {evidence_tier}",

                "Independent TPS and TVS assessments jointly determine the institutional opinion presented in this report.",

            ],

            title="Institutional Claim Snapshot",

        )

    )

    story.extend(

        build_callout(

            "Institutional Assessment Scope",

            (

                "This report is intended for institutional "

                "allocators, auditors, counterparties and "

                "independent reviewers requiring an objective "

                "assessment of both trading performance and "

                "verification credibility. Every conclusion "

                "presented in subsequent chapters originates "

                "from canonical TPS and TVS computations."

            ),

        )

    )

    #
    # Executive Dashboard
    #

    dashboard = [

        ["Executive Metric", "Result"],

        [
            "Institutional Decision",
            verification.decision,
        ],

        [
            "Verification Status",
            str(verification.verification_status).title(),
        ],

        [
            "Verification Score",
            f"{verification.verification_score:.1f}/100",
        ],

        [
            "Institutional Confidence",
            (
                f"{verification.confidence * 100:.1f}%"
                if verification.confidence <= 1
                else f"{verification.confidence:.1f}%"
            ),
        ],

        [
            "Verification Band",
            verification.verification_band,
        ],

        [
            "Performance Band",
            assessment.get(
                "performance_band",
                "Not Available",
            ),
        ],

        [
            "Verified Trades",
            summary.get(
                "trade_count",
                "Not Available",
            ),
        ],

    ]

    story.extend(

        build_metric_block(

            "Executive Dashboard",

            build_metric_table(
                dashboard,
            ),

        )

    )

    story.extend(

        build_findings(

            [

                (
                    f"The submitted trading claim received an institutional "
                    f"decision of {verification.decision} with a "
                    f"{verification.verification_band} verification classification."
                ),

                (
                    f"The historical trading record comprises "
                    f"{summary.get('trade_count', 'Not Available')} verified trades "
                    f"and achieved a "
                    f"{assessment.get('performance_band', 'Not Available')} "
                    f"performance assessment."
                ),

                (
                    "Independent assessments of trading performance, "
                    "evidence quality, governance controls and audit "
                    "lineage collectively support the institutional "
                    "opinion presented throughout this report."
                ),

            ],

            title="Executive Opinion",

        )

    )

    return story