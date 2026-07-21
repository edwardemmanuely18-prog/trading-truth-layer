"""
Trading Truth Layer

Volume IV

Institutional Evidence Infrastructure
(Evidence Intake)

Institutional Domain II
"""

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


def build_domain_2_evidence_intake():

    """
    Builds Domain II documentation for the
    Institutional Evidence Infrastructure.
    """

    story = []

    # --------------------------------------------------
    # DOMAIN TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN II",
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
            "INSTITUTIONAL EVIDENCE INFRASTRUCTURE",
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
            "(EVIDENCE INTAKE)",
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
            "Institutional trust begins with institutional evidence.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Institutional Evidence Infrastructure provides the "
            "institutional intake capabilities required to acquire, "
            "synchronize and govern trading evidence throughout the "
            "Trading Truth Layer trust lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every institutional workflow inside Trading Truth Layer "
            "begins at the Institutional Evidence Infrastructure.",
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
    # WHY DOES IT EXIST?
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHY DOES IT EXIST?",
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
            "Institutional performance cannot be verified without "
            "institutional evidence.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Evidence Infrastructure exists to ensure that trading "
            "records enter the TTL ecosystem through governed evidence "
            "acquisition processes.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It establishes the provenance, trust tier and acquisition "
            "methodology required for institutional verification.",
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
    # WHICH INSTITUTIONAL PROBLEMS DOES IT SOLVE?
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHICH INSTITUTIONAL PROBLEMS DOES IT SOLVE?",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    problems = [

        "Unverified trading record acquisition.",

        "Unknown evidence provenance.",

        "Fragmented broker integrations.",

        "Historical trade import limitations.",

        "Institutional synchronization challenges.",

        "Evidence trust tier uncertainty.",

        "Evidence governance deficiencies.",

    ]

    for problem in problems:

        story.append(
            Paragraph(
                f"• {problem}",
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
    # INSTITUTIONAL EVIDENCE TRUST HIERARCHY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL EVIDENCE TRUST HIERARCHY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    trust_tiers = [

        "Tier I - Live Broker API Evidence.",

        "Tier II - Historical Broker File Evidence.",

        "Tier III - Manual Evidence Records.",

    ]

    for tier in trust_tiers:

        story.append(
            Paragraph(
                f"• {tier}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Tier I evidence represents the highest institutional "
            "trust tier while Tier III evidence represents manually "
            "generated evidence requiring additional institutional "
            "scrutiny.",
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
    # INSTITUTIONAL EVIDENCE INTEGRITY RULES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL EVIDENCE INTEGRITY RULES",
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
            "Trading Truth Layer preserves evidence provenance "
            "throughout the institutional trust lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Evidence trust tiers are assigned according to the "
            "original source of the trading records and are "
            "continuously governed throughout the verification process.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Any modification performed on broker-originated evidence "
            "automatically alters its institutional provenance and may "
            "result in trust tier reclassification.",
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

        "Broker Connections",

        "Import Center",

        "Sync Center",

        "Adapter Registry",

    ]

    for subdomain in subdomains:

        story.append(
            Paragraph(
                f"• {subdomain}",
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
    # BROKER CONNECTIONS
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "BROKER CONNECTIONS",
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
            "The Broker Connections subdomain provides institutional "
            "broker connectivity capabilities for supported trading "
            "providers.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Users may establish institutional-grade broker "
            "connections for evidence synchronization and verification.",
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
    # IMPORT CENTER
    # --------------------------------------------------

    story.append(
        Paragraph(
            "IMPORT CENTER",
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
            "The Import Center provides historical evidence import "
            "capabilities for supported broker exports and institutional "
            "evidence files.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Imported records enter the TTL evidence governance "
            "workflow for institutional trust assessment.",
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
    # SYNC CENTER
    # --------------------------------------------------

    story.append(
        Paragraph(
            "SYNC CENTER",
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
            "The Sync Center provides institutional synchronization "
            "capabilities for connected broker accounts.",
            BODY_STYLE,
        )
    )

    sync_types = [

        "Historical Trades.",

        "Incremental Trades.",

        "Open Positions.",

        "Account State Snapshots.",

    ]

    for sync_type in sync_types:

        story.append(
            Paragraph(
                f"• {sync_type}",
                BODY_STYLE,
            )
        )

    story.append(
       Paragraph(
            "All synchronized evidence is persisted within the "
            "canonical evidence infrastructure for downstream "
            "verification workflows.",
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
    # ADAPTER REGISTRY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "ADAPTER REGISTRY",
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
            "The Adapter Registry provides institutional visibility "
            "into supported evidence providers and connectivity "
            "capabilities.",
            BODY_STYLE,
        )
    )

    adapter_questions = [

        "Which broker adapters are operational?",

        "Which providers support live synchronization?",

        "Which providers support historical imports?",

        "Which trust tier has been assigned?",

        "Which providers are planned?",

    ]

    for question in adapter_questions:

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
    # INSTITUTIONAL POSITIONING
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INSTITUTIONAL POSITIONING",
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
            "The Institutional Evidence Infrastructure is the entry "
            "point of the institutional trust lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "No institutional verification may occur before evidence "
            "has been successfully acquired and governed.",
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
    # INSTITUTIONAL OUTPUTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL OUTPUTS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    outputs = [

        "Institutional evidence records.",

        "Broker synchronization jobs.",

        "Evidence trust tier assignments.",

        "Historical trade imports.",

        "Institutional provenance metadata.",

        "Canonical evidence acquisition records.",

    ]

    for output in outputs:

        story.append(
            Paragraph(
                f"• {output}",
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
    # INSTITUTIONAL QUESTIONS ANSWERED
    # --------------------------------------------------

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

        "Where did the trading evidence originate?",

        "Can the broker source be trusted?",

        "What trust tier was assigned?",

        "Was synchronization successful?",

        "Has evidence provenance been preserved?",

        "Which broker integrations are supported?",

        "Has institutional evidence entered the TTL workflow?",

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
    # TTL WORKFLOW POSITION
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "TTL WORKFLOW POSITION",
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

        "Institutional Evidence Acquisition",

        "Institutional Evidence Governance",

        "Canonical Evidence Infrastructure",

        "Claim Infrastructure",

        "Institutional Verification Workflow",

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
    # FUTURE CAPABILITIES
    # --------------------------------------------------

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

        "Additional institutional broker integrations.",

        "Expanded synchronization capabilities.",

        "Enhanced evidence provenance intelligence.",

        "Institutional evidence scoring systems.",

        "Automated broker capability detection.",

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
            "The Institutional Evidence Infrastructure is responsible "
            "for acquiring, synchronizing and governing institutional "
            "trading evidence within Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It establishes the institutional provenance, trust tier "
            "and acquisition methodology required for institutional "
            "verification and trust manufacturing.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every institutional trust workflow begins with evidence.",
            BODY_STYLE,
        )
    )

    # --------------------------------------------------
    # PAGE BREAK
    # --------------------------------------------------

    story.append(
        PageBreak()
    )

    return story


# ==========================================================
# END OF FILE
# ==========================================================