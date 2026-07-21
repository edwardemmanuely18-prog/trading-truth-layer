from reportlab.platypus import (
    Paragraph,
    Spacer,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    SUBTITLE_STYLE,
    BODY_STYLE,
    BODY_CENTER_STYLE,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_domain_5_trust_intelligence():

    """
    Builds Domain V documentation for the
    Institutional Trust Intelligence Infrastructure.
    """

    story = []

    # --------------------------------------------------
    # DOMAIN TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN V",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "INSTITUTIONAL TRUST INTELLIGENCE INFRASTRUCTURE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "(TRUST INTELLIGENCE)",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # WHAT IS THE INFRASTRUCTURE?
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHAT IS THE INFRASTRUCTURE?",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Institutional Trust Intelligence Infrastructure is "
            "the institutional intelligence layer responsible for "
            "converting verification records, evidence quality, "
            "lifecycle governance, integrity monitoring and risk "
            "analytics into allocator-grade trust intelligence.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Trust Intelligence does not create claims and does not "
            "participate in evidence ingestion.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Its responsibility is institutional assessment of the "
            "verification ecosystem operating inside a workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "All Trust Intelligence metrics are produced from "
            "canonical verification infrastructure and Trading "
            "Verification System outputs.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PRIMARY RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PRIMARY RESPONSIBILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    responsibilities = [

        "Trust quality.",

        "Verification maturity.",

        "Lifecycle governance.",

        "Integrity posture.",

        "Evidence quality.",

        "Risk posture.",

        "Due diligence readiness.",

        "Institutional reporting readiness.",

        "Workspace trust health.",

        "Institutional ranking intelligence.",

    ]

    for responsibility in responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL SUBDOMAINS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL SUBDOMAINS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    subdomains = [

        "Trust Scores.",

        "Leaderboards.",

        "Verification Analytics.",

        "Integrity Analytics.",

        "Evidence Analytics.",

        "Risk Analytics.",

        "Due Diligence Reports.",

        "Report Center.",

    ]

    for subdomain in subdomains:

        story.append(
            Paragraph(
                f"• {subdomain}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "These institutional surfaces collectively represent "
            "the Trust Intelligence Engine of Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # TRUST SCORES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TRUST SCORES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Trust Scores page is the institutional trust "
            "ranking engine of Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Trust scores are generated using institutional "
            "verification signals derived from the Trading "
            "Verification System.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Trust Scores provide institutional visibility into "
            "the trust quality of all claims inside a workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # TRUST SCORE SIGNALS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TRUST SCORE SIGNALS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    trust_signals = [

        "Lifecycle integrity.",

        "Verification status.",

        "Publication status.",

        "Lock status.",

        "Independent review activity.",

        "Governance posture.",

        "Network trust.",

        "Verification maturity.",

        "Trading Verification System outputs.",

    ]

    for signal in trust_signals:

        story.append(
            Paragraph(
                f"• {signal}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL GRADING FRAMEWORK
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL GRADING FRAMEWORK",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Trading Truth Layer utilizes a standardized "
            "institutional grading framework throughout all "
            "Trust Intelligence, Investigation and Public Trust "
            "surfaces.",
            BODY_STYLE,
        )
    )

    grades = [

        "Elite.",

        "Institutional.",

        "Verified.",

        "Trusted.",

        "Developing.",

        "Limited.",

    ]

    for grade in grades:

        story.append(
            Paragraph(
                f"• {grade}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    grade_definitions = [

        "ELITE - Exceptional institutional-grade confidence.",

        "INSTITUTIONAL - Strong institutional confidence.",

        "VERIFIED - Highly credible verified claim.",

        "TRUSTED - Good verification confidence.",

        "DEVELOPING - Verification maturity is improving.",

        "LIMITED - Limited verification confidence.",

    ]

    for definition in grade_definitions:

        story.append(
            Paragraph(
                f"• {definition}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # TRUST SCORE RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TRUST SCORE RESPONSIBILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    trust_metrics = [

        "Average Trust Score.",

        "Average Network Score.",

        "Workspace Institutional Grade.",

        "Verification Statistics.",

        "Trust Maturity Analytics.",

        "Network Trust Metrics.",

    ]

    for metric in trust_metrics:

        story.append(
            Paragraph(
                f"• {metric}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Trust metrics are aggregated across all claims "
            "inside the workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # VERIFICATION REGISTRY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION REGISTRY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Verification Registry is powered by the Trading "
            "Verification System.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every verification decision produced by TVS is "
            "preserved inside the registry.",
            BODY_STYLE,
        )
    )

    registry_fields = [

        "Rank.",

        "Claim.",

        "Trust Score.",

        "Institutional Tier.",

        "Lifecycle Status.",

        "Review Count.",

        "Rating Score.",

    ]

    for field in registry_fields:

        story.append(
            Paragraph(
                f"• {field}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Verification Registry represents the canonical "
            "trust status of every claim operating inside the "
            "workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # LEADERBOARDS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "LEADERBOARDS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Leaderboards subdomain provides institutional "
            "ranking capabilities across all verification records "
            "contained within a workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Leaderboards allow institutions to identify the "
            "highest quality verification records according to "
            "institutional trust metrics.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # CLAIM RANKINGS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CLAIM RANKINGS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    claim_rankings = [

        "Trust Score.",

        "Verification Score.",

        "Institutional Grade.",

        "Verification Status.",

        "Review Activity.",

        "Public Trust Status.",

    ]

    for ranking in claim_rankings:

        story.append(
            Paragraph(
                f"• {ranking}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Claim rankings provide allocator-grade visibility "
            "into institutional trust quality across all verified "
            "claims.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # MEMBER RANKINGS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "MEMBER RANKINGS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    member_rankings = [

        "Member Trust Score.",

        "Verification Coverage.",

        "Institutional Grade.",

        "Verification Maturity.",

        "Performance Contribution.",

        "Trust Intelligence Metrics.",

    ]

    for ranking in member_rankings:

        story.append(
            Paragraph(
                f"• {ranking}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Member rankings provide institutional visibility into "
            "the trust posture of individual contributors inside a "
            "workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # VERIFICATION ANALYTICS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION ANALYTICS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Verification Analytics provides institutional "
            "visibility into verification coverage, lifecycle "
            "progression and trust maturity across a workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Verification Analytics consumes Trading Verification "
            "System outputs to produce allocator-grade verification "
            "intelligence.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # VERIFICATION RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION RESPONSIBILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    verification_responsibilities = [

        "Verification coverage monitoring.",

        "Lifecycle progression monitoring.",

        "Verification maturity monitoring.",

        "Trust intelligence analytics.",

        "Institutional trust reporting.",

        "Workspace verification health monitoring.",

    ]

    for responsibility in verification_responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # VERIFICATION ACTIVITY FEED
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "VERIFICATION ACTIVITY FEED",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    activity_feed = [

        "Verification events.",

        "Publication events.",

        "Lock events.",

        "Review events.",

        "Trust score updates.",

        "Verification lifecycle changes.",

    ]

    for item in activity_feed:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Verification Activity Feed provides a historical "
            "record of institutional verification operations.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INTEGRITY ANALYTICS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INTEGRITY ANALYTICS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Integrity Analytics provides institutional integrity "
            "monitoring capabilities across the verification "
            "ecosystem.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Integrity Analytics identifies integrity exceptions, "
            "trust posture changes and governance concerns before "
            "they affect institutional trust.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL INTEGRITY SCANNERS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL INTEGRITY SCANNERS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    scanners = [

        "Lifecycle integrity monitoring.",

        "Trust posture monitoring.",

        "Verification maturity monitoring.",

        "Evidence integrity monitoring.",

        "Governance compliance monitoring.",

        "Verification status monitoring.",

    ]

    for scanner in scanners:

        story.append(
            Paragraph(
                f"• {scanner}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INTEGRITY RESPONSIBILITIES
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INTEGRITY RESPONSIBILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    integrity_responsibilities = [

        "Integrity scoring.",

        "Governance monitoring.",

        "Institutional health monitoring.",

        "Verification integrity monitoring.",

        "Trust maturity analytics.",

        "Allocator-grade trust intelligence.",

    ]

    for responsibility in integrity_responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # FINDING OPERATIONS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "FINDING OPERATIONS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Institutional findings are generated whenever Trust "
            "Intelligence identifies material verification, "
            "integrity or governance observations.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Findings are utilized throughout allocator reports, "
            "institutional reviews and due diligence workflows.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # SCAN HISTORY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "SCAN HISTORY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    scan_history = [

        "Integrity scans.",

        "Verification scans.",

        "Trust intelligence scans.",

        "Risk scans.",

        "Evidence quality scans.",

        "Institutional review scans.",

    ]

    for item in scan_history:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Scan History preserves an institutional audit trail of "
            "all Trust Intelligence assessment activities performed "
            "within a workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # EVIDENCE ANALYTICS
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "EVIDENCE ANALYTICS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Evidence Analytics provides institutional intelligence "
            "regarding the quality, provenance and verification "
            "readiness of trading evidence operating inside a "
            "workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Institutional evidence quality directly influences "
            "verification confidence and allocator trust.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # EVIDENCE QUALITY ENGINE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "EVIDENCE QUALITY ENGINE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    evidence_quality_metrics = [

        "Trust tier coverage.",

        "Evidence provenance quality.",

        "Verification readiness.",

        "Evidence completeness.",

        "Canonical evidence health.",

        "Institutional evidence maturity.",

    ]

    for metric in evidence_quality_metrics:

        story.append(
            Paragraph(
                f"• {metric}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Evidence Quality Engine continuously evaluates "
            "institutional evidence quality throughout the trust "
            "lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # EVIDENCE EXCEPTIONS REGISTRY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "EVIDENCE EXCEPTIONS REGISTRY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    exception_types = [

        "Missing evidence records.",

        "Trust tier inconsistencies.",

        "Verification exceptions.",

        "Integrity exceptions.",

        "Evidence provenance issues.",

        "Institutional governance exceptions.",

    ]

    for item in exception_types:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Institutional evidence exceptions are preserved for "
            "allocator due diligence and institutional reviews.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # EVIDENCE MONITORING FEED
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "EVIDENCE MONITORING FEED",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    monitoring_items = [

        "Evidence health changes.",

        "Verification readiness changes.",

        "Trust tier changes.",

        "Integrity alerts.",

        "Evidence lifecycle events.",

        "Institutional quality alerts.",

    ]

    for item in monitoring_items:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Evidence Monitoring Feed provides continuous "
            "institutional visibility into the health of canonical "
            "evidence records.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # RISK ANALYTICS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "RISK ANALYTICS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Risk Analytics provides institutional visibility into "
            "verification risk, governance risk and evidence risk "
            "throughout the TTL ecosystem.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Institutional risk intelligence is a critical component "
            "of allocator due diligence processes.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # RISK RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "RISK RESPONSIBILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    risk_metrics = [

        "Verification risk.",

        "Integrity risk.",

        "Governance risk.",

        "Evidence risk.",

        "Lifecycle risk.",

        "Institutional trust risk.",

        "Allocator risk intelligence.",

    ]

    for metric in risk_metrics:

        story.append(
            Paragraph(
                f"• {metric}",
                BODY_STYLE,
            )
        )

    story.append(
       Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # CLAIM RISK FEED
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "CLAIM RISK FEED",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    claim_risk_items = [

        "Claim governance concerns.",

        "Verification maturity concerns.",

        "Evidence quality concerns.",

        "Integrity concerns.",

        "Lifecycle anomalies.",

        "Institutional trust warnings.",

    ]

    for item in claim_risk_items:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
       Paragraph(
            "The Claim Risk Feed continuously monitors institutional "
            "risk signals generated throughout the verification "
            "lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # DUE DILIGENCE REPORTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DUE DILIGENCE REPORTS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Due Diligence Reports subdomain provides allocator-"
            "grade institutional assessments across all trust "
            "intelligence surfaces.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Institutional reports are designed to assist allocators, "
            "institutions and reviewers in making evidence-based "
            "capital allocation decisions.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL ASSESSMENT AREAS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL ASSESSMENT AREAS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    assessment_areas = [

        "Verification quality.",

        "Institutional integrity.",

        "Evidence quality.",

        "Risk posture.",

        "Lifecycle governance.",

        "Public trust readiness.",

        "Allocator readiness.",

    ]

    for area in assessment_areas:

        story.append(
            Paragraph(
                f"• {area}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # DETAILED INSTITUTIONAL REVIEWS
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "DETAILED INSTITUTIONAL REVIEWS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    reviews = [

        "Verification reviews.",

        "Integrity reviews.",

        "Evidence reviews.",

        "Risk reviews.",

        "Trust intelligence reviews.",

        "Institutional allocator reviews.",

    ]

    for review in reviews:

        story.append(
            Paragraph(
                f"• {review}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "These institutional reviews collectively establish the "
            "allocator-grade due diligence capabilities of Trading "
            "Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

        # --------------------------------------------------
    # REPORT CENTER
    # --------------------------------------------------

    story.append(
        Paragraph(
            "REPORT CENTER",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Report Center provides allocator-grade institutional "
            "reporting capabilities across all Trust Intelligence "
            "surfaces operating inside Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Institutional reports consolidate verification, "
            "integrity, evidence and risk intelligence into "
            "decision-ready capital allocation artifacts.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # REPORT CENTER RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "REPORT CENTER RESPONSIBILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    report_responsibilities = [

        "Allocator report generation.",

        "Verification report generation.",

        "Institutional due diligence reports.",

        "Trust intelligence reports.",

        "Risk assessment reports.",

        "Institutional review reports.",

    ]

    for responsibility in report_responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # CLAIM EXPORT INFRASTRUCTURE
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "CLAIM EXPORT INFRASTRUCTURE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    export_capabilities = [

        "Institutional PDF exports.",

        "Allocator-ready exports.",

        "Verification exports.",

        "Institutional review exports.",

        "Evidence intelligence exports.",

        "Due diligence exports.",

    ]

    for capability in export_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Institutional exports preserve the trust intelligence "
            "produced throughout the TTL ecosystem and enable "
            "allocator-grade reporting workflows.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL WORKFLOW
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL WORKFLOW",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    workflow = [

        "Canonical Evidence Infrastructure",

        "Claim Governance Infrastructure",

        "Trading Verification System",

        "Trust Intelligence Infrastructure",

        "Institutional Investigation Infrastructure",

        "Public Trust Infrastructure",

    ]

    for item in workflow:

        story.append(
            Paragraph(
                item,
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_MD,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL QUESTIONS ANSWERED
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INSTITUTIONAL QUESTIONS ANSWERED",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    questions = [

        "Can this claim be institutionally trusted?",

        "Is the verification posture sufficient for capital allocation?",

        "Is the evidence of institutional quality?",

        "What institutional risks are present?",

        "Has lifecycle governance been preserved?",

        "Is the claim allocator-ready?",

        "Does the workspace satisfy institutional standards?",

        "What trust intelligence findings have been identified?",

    ]

    for question in questions:

        story.append(
            Paragraph(
                f"• {question}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # DOMAIN V ARCHITECTURE STATUS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN V ARCHITECTURE STATUS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    architecture_components = [

        "Trust Scores.",

        "Leaderboards.",

        "Verification Analytics.",

        "Integrity Analytics.",

        "Evidence Analytics.",

        "Risk Analytics.",

        "Due Diligence Reports.",

        "Report Center.",

    ]

    for component in architecture_components:

        story.append(
            Paragraph(
                f"• {component}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "These institutional intelligence capabilities "
            "collectively establish the Trust Intelligence "
            "Infrastructure of Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # FUTURE INFRASTRUCTURE CAPABILITIES
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "FUTURE INFRASTRUCTURE CAPABILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    future_capabilities = [

        "Advanced institutional scoring models.",

        "Cross-workspace trust intelligence.",

        "Allocator intelligence automation.",

        "Institutional benchmark analytics.",

        "Global trust intelligence rankings.",

        "Automated institutional due diligence workflows.",

        "Institutional capital allocation intelligence.",

    ]

    for capability in future_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # ARCHITECTURE SUMMARY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "ARCHITECTURE SUMMARY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Institutional Trust Intelligence Infrastructure "
            "is responsible for transforming verification records "
            "into allocator-grade trust intelligence.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It provides institutional visibility into trust "
            "quality, evidence quality, integrity posture, risk "
            "analytics and due diligence readiness throughout the "
            "Trading Truth Layer ecosystem.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Trust Intelligence represents the institutional "
            "decision-making layer that enables evidence-based "
            "capital allocation.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PAGE BREAK
    # --------------------------------------------------

    story.append(
        PageBreak()
    )

    return story