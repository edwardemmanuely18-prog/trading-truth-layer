"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

Institutional Evidence Acquisition
"""

from reportlab.platypus import (
    Paragraph,
    Spacer,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    BODY_STYLE,
    BODY_CENTER_STYLE,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_evidence_acquisition():

    """
    Builds the Institutional Evidence
    Acquisition section for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL EVIDENCE ACQUISITION",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INTRODUCTION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional trust begins with "
            "institutional evidence.",
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
        Paragraph(
            "Before trading activity can be "
            "verified, Trading Truth Layer must "
            "first acquire and govern the "
            "underlying trading evidence.",
            BODY_STYLE,
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
            "Institutional Evidence Acquisition "
            "provides the capabilities required "
            "to transform broker-originated "
            "trading activity into canonical "
            "institutional evidence.",
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
    # PRIMARY OBJECTIVES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PRIMARY OBJECTIVES",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    objectives = [

        "Acquire institutional trading evidence.",

        "Preserve broker provenance.",

        "Govern evidence intake workflows.",

        "Assign institutional trust tiers.",

        "Normalize trading records.",

        "Generate canonical institutional evidence.",

    ]

    for objective in objectives:

        story.append(
            Paragraph(
                f"• {objective}",
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_MD,
            )
        )

    # --------------------------------------------------
    # EVIDENCE SOURCES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "SUPPORTED EVIDENCE SOURCES",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    sources = [

        "Live broker API synchronization.",

        "Historical broker file imports.",

        "Institutional synchronization jobs.",

        "Supported broker adapters.",

        "Manual institutional evidence records.",

    ]

    for source in sources:

        story.append(
            Paragraph(
                f"• {source}",
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_MD,
            )
        )

    # --------------------------------------------------
    # GOVERNANCE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL EVIDENCE GOVERNANCE",
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
        Paragraph(
            "Trading Truth Layer preserves "
            "institutional evidence provenance "
            "throughout the entire verification "
            "lifecycle.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    governance_items = [

        "Evidence provenance.",

        "Trust tier assignments.",

        "Broker source integrity.",

        "Synchronization records.",

        "Historical acquisition records.",

        "Institutional governance policies.",

    ]

    for item in governance_items:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_MD,
            )
        )

    # --------------------------------------------------
    # INSTITUTIONAL QUESTIONS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional Questions Answered",
            BODY_CENTER_STYLE,
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

        "Can the source of evidence be trusted?",

        "Which trust tier has been assigned?",

        "Has the evidence been institutionally governed?",

        "Can the trading activity proceed to verification?",

    ]

    for question in questions:

        story.append(
            Paragraph(
                f"• {question}",
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_MD,
            )
        )

    # --------------------------------------------------
    # TTL WORKFLOW POSITION
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "TTL WORKFLOW POSITION",
            BODY_CENTER_STYLE,
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

        "↓",

        "Evidence Governance",

        "↓",

        "Canonical Institutional Evidence",

        "↓",

        "Trading Verification",

        "↓",

        "Institutional Trust",

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