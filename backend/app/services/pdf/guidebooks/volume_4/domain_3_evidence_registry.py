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


def build_domain_3_evidence_registry():

    """
    Builds Domain III documentation for the
    Canonical Evidence Infrastructure.
    """

    story = []

    # --------------------------------------------------
    # DOMAIN TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN III",
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
            "CANONICAL EVIDENCE INFRASTRUCTURE",
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
            "(EVIDENCE REGISTRY)",
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
            "The Canonical Evidence Infrastructure serves as the "
            "institutional single source of truth for all trading "
            "evidence inside Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every trade record that enters the TTL trust workflow is "
            "governed, preserved, classified, audited and protected "
            "within the Canonical Evidence Infrastructure before it "
            "participates in institutional verification.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "This infrastructure guarantees that institutional "
            "evidence maintains its provenance, integrity and "
            "governance posture throughout the entire trust lifecycle.",
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
            "Institutional trust cannot exist without a canonical "
            "source of truth for trading evidence.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Canonical Evidence Infrastructure exists to preserve "
            "institutional evidence after acquisition and before "
            "verification.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It establishes the institutional governance layer "
            "required for evidence immutability, provenance "
            "preservation and cryptographic integrity protection.",
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

        "Fragmented trading evidence.",

        "Unknown evidence provenance.",

        "Lack of canonical trade records.",

        "Poor evidence governance.",

        "Untracked import operations.",

        "Missing audit capabilities.",

        "Insufficient integrity protection.",

        "Institutional immutability challenges.",

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
    # CANONICAL EVIDENCE INTEGRITY PRINCIPLES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CANONICAL EVIDENCE INTEGRITY PRINCIPLES",
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
            "Trading Truth Layer preserves canonical evidence "
            "throughout the institutional trust lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "All canonical trade records maintain their provenance, "
            "trust tier assignments and institutional classifications.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Trades belonging to locked claims are institutionally "
            "immutable and cannot be edited, modified or reclassified.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Cryptographic integrity mechanisms ensure that canonical "
            "evidence maintains institutional trust characteristics "
            "throughout downstream verification workflows.",
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

        "Canonical Trade Ledger",

        "Evidence Records",

        "Import Batches",

        "Audit Timeline",

        "Integrity Registry",

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
    # CANONICAL TRADE LEDGER
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CANONICAL TRADE LEDGER",
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
            "The Canonical Trade Ledger serves as the institutional "
            "source of truth for all trading records inside a "
            "workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Trading records are normalized into canonical evidence "
            "records after institutional evidence intake.",
            BODY_STYLE,
        )
    )

    ledger_sources = [

        "Live broker synchronization.",

        "Historical trade imports.",

        "Manual trade records.",

    ]

    for item in ledger_sources:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Institutional strategy performance metrics are therefore "
            "produced from canonical evidence rather than user "
            "reported claims.",
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
    # EVIDENCE RECORDS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "EVIDENCE RECORDS",
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
            "The Evidence Records subdomain provides institutional "
            "classification capabilities for canonical evidence.",
            BODY_STYLE,
        )
    )

    classifications = [

        "Verification status.",

        "Trust tier.",

        "Evidence provenance.",

        "Institutional source.",

    ]

    for item in classifications:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Institutions may therefore assess the quality and trust "
            "profile of all evidence contained within a workspace.",
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
    # IMPORT BATCHES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "IMPORT BATCHES",
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
            "The Import Batches subdomain provides institutional "
            "ingestion audit capabilities for historical evidence.",
            BODY_STYLE,
        )
    )

    batch_items = [

        "Batch identifiers.",

        "Source providers.",

        "Imported files.",

        "Received records.",

        "Imported records.",

        "Rejected records.",

        "Duplicate records.",

        "Creation timestamps.",

    ]

    for item in batch_items:

        story.append(
            Paragraph(
                f"• {item}",
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
    # AUDIT TIMELINE
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "AUDIT TIMELINE",
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
            "The Audit Timeline provides an immutable institutional "
            "workspace governance timeline.",
            BODY_STYLE,
        )
    )

    audit_events = [

        "Claim operations.",

        "Verification events.",

        "Publication events.",

        "Locking events.",

        "Import events.",

        "Dispute events.",

        "Governance events.",

    ]

    for item in audit_events:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Audit Timeline preserves a historical record of all "
            "institutional activities performed throughout the trust "
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
    # INTEGRITY REGISTRY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INTEGRITY REGISTRY",
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
            "The Integrity Registry provides institutional "
            "cryptographic integrity capabilities for canonical "
            "evidence.",
            BODY_STYLE,
        )
    )

    integrity_items = [

        "Evidence fingerprints.",

        "Cryptographic hashes.",

        "Trust tier assignments.",

        "Evidence provenance.",

        "Broker references.",

        "Integrity coverage.",

        "Verification status.",

    ]

    for item in integrity_items:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Integrity Registry ensures that institutional "
            "evidence maintains cryptographic integrity throughout "
            "the entire TTL trust workflow.",
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
            "The Canonical Evidence Infrastructure serves as the "
            "institutional source of truth positioned immediately "
            "after evidence intake.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "All institutional verification capabilities depend upon "
            "the integrity and governance guarantees provided by this "
            "infrastructure.",
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

        "Canonical trade records.",

        "Institutional provenance metadata.",

        "Import batch audit records.",

        "Workspace governance events.",

        "Evidence integrity records.",

        "Trust tier classifications.",

    ]

    for item in outputs:

        story.append(
            Paragraph(
                f"• {item}",
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

        "Which trades constitute the institutional source of truth?",

        "Where did the evidence originate?",

        "Has the evidence been modified?",

        "Is the evidence immutable?",

        "What trust tier was assigned?",

        "Which import batch introduced the evidence?",

        "What governance events occurred?",

        "Is the evidence cryptographically protected?",

        "Does the evidence preserve institutional integrity?",

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

        "Institutional Evidence Intake",

        "Canonical Evidence Infrastructure",

        "Claim Infrastructure",

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
    # FUTURE INFRASTRUCTURE CAPABILITIES
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

    capabilities = [

        "Expanded evidence intelligence capabilities.",

        "Advanced integrity verification systems.",

        "Institutional provenance analytics.",

        "Enhanced governance automation.",

        "Evidence immutability monitoring.",

    ]

    for item in capabilities:

        story.append(
            Paragraph(
                f"• {item}",
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
            "The Canonical Evidence Infrastructure is responsible "
            "for preserving, governing and protecting institutional "
            "trading evidence throughout the TTL trust lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It establishes the institutional source of truth that "
            "supports downstream claim verification, trust "
            "intelligence and public trust manufacturing.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every institutional verification workflow depends upon "
            "the integrity of canonical evidence.",
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