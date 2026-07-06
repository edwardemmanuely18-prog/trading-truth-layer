from __future__ import annotations

from app.services.pdf.common.institutional_sections import (
    build_section,
    build_callout,
    build_narrative,
    build_observations,
    build_recommendations,
)

# ==========================================================
# FINDINGS
# ==========================================================

def build_findings_section(report):
    """
    Institutional Findings.

    Synthesizes the analytical sections into
    allocator-facing conclusions.

    No calculations are performed here.
    """

    allocator = report["allocator_assessment"]

    performance = report["performance"]

    risk = report["risk"]

    workspace = report["workspace_verification"]

    certificates = report.get(
        "workspace_certificates",
        [],
    )

    story = []

    #
    # Narrative
    #

    story.extend(

        build_section(

            "Institutional Findings",

            build_narrative(

                """
                This section consolidates the
                principal institutional observations
                derived from trading analytics and
                the Trading Verification System.

                The objective is to summarize the
                most relevant strengths, operational
                observations and allocator
                considerations before the final
                verdict.
                """

            ),

        )

    )

    #
    # Strengths
    #

    strengths = []

    if performance.get("performance_band") == "STRONG":
        strengths.append(
            "Historical trading performance demonstrates institutional-grade profitability."
        )

    if workspace.average_verification_score >= 85:
        strengths.append(
            "Verification confidence exceeds institutional acceptance thresholds."
        )

    if workspace.claim_count >= 10:

        strengths.append(
            "Verification confidence is supported by a substantial portfolio of certified claims."
        )

    if allocator.get("allocator_score", 0) >= 85:
        strengths.append(
            "Allocator assessment supports institutional capital review."
        )

    if not strengths:
        strengths.append(
            "No exceptional institutional strengths were identified beyond baseline compliance."
        )

    from app.services.pdf.common.institutional_sections import build_findings

    story.extend(
        build_findings(
            strengths
        )
    )

    risks = report["allocator_risks"]["items"]

    if risks:

        formatted = [
            r.replace("_", " ").title()
            for r in risks
        ]

        story.extend(

            build_section(

                "Operational Risks",

                build_observations(
                    formatted
                ),

            )

        )

    #
    # Operational Observations
    #

    observations = [

        f"Allocator Score: {allocator.get('allocator_score','-')}",

        f"Performance Band: {performance.get('performance_band','-')}",

        f"Risk Band: {risk.get('risk_band','-')}",

        f"Verification Band: {workspace.verification_band}",

    ]

    story.extend(

        build_section(

            "Operational Summary",

            build_findings(
                observations
            ),

        )

    )

    #
    # Recommendations
    #

    recommendations = []

    score = allocator.get(
        "allocator_score",
        0,
    )

    if score >= 85:

        recommendations.extend([

            "Maintain current governance controls.",

            "Continue periodic TVS verification.",

            "Preserve evidence provenance.",

        ])

    elif score >= 70:

        recommendations.extend([

            "Increase verification coverage.",

            "Improve governance maturity.",

            "Continue accumulating verified trading history.",

        ])

    else:

        recommendations.extend([

            "Address operational weaknesses before allocator review.",

            "Improve verification quality.",

            "Generate a new allocator assessment after corrective actions.",

        ])

    story.extend(

        build_recommendations(

            recommendations,

        )

    )

    #
    # Executive Finding
    #

    story.extend(

        build_callout(

            "Executive Finding",

            (
                "The allocator assessment represents "
                "a combined evaluation of trading "
                "performance, downside risk and the "
                "Trading Verification System. "
                "Institutional capital allocation "
                "decisions should consider the entire "
                "verification profile rather than "
                "individual metrics in isolation."
            ),

        )

    )

    return story