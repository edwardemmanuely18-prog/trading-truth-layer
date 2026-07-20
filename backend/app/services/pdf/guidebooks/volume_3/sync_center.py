"""
Trading Truth Layer

Volume III

Institutional Evidence Infrastructure

Sync Center
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


def build_sync_center():

    """
    Builds the Sync Center section for
    Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "SYNC CENTER",
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
            "The Sync Center provides institutional "
            "trade synchronization capabilities for "
            "connected broker accounts.",
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
            "Once a broker account has been "
            "successfully connected and verified, "
            "Trading Truth Layer may directly "
            "acquire institutional trading evidence "
            "from supported providers through "
            "governed synchronization jobs.",
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
            "The Sync Center transforms broker-"
            "originated trading activity into "
            "canonical institutional evidence "
            "capable of supporting verification "
            "and institutional due diligence.",
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
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    responsibilities = [

        "Historical trade synchronization.",

        "Incremental trade synchronization.",

        "Open position synchronization.",

        "Account state snapshot synchronization.",

        "Synchronization governance.",

        "Evidence acquisition management.",

        "Synchronization status monitoring.",

        "Canonical evidence persistence.",

    ]

    for responsibility in responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
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
    # SYNCHRONIZATION CATEGORIES
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INSTITUTIONAL SYNCHRONIZATION CATEGORIES",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    synchronization_categories = [

        (
            "Historical Trades",
            "Provides complete historical trading "
            "records directly from supported "
            "broker providers."
        ),

        (
            "Incremental Trades",
            "Provides synchronization of newly "
            "executed trading activity following "
            "the initial synchronization process."
        ),

        (
            "Open Positions",
            "Provides synchronization of currently "
            "active broker positions for supported "
            "providers."
        ),

        (
            "Account State Snapshots",
            "Provides institutional account-level "
            "snapshots representing the current "
            "state of the connected broker account."
        ),

    ]

    for title, description in synchronization_categories:

        story.append(
            Paragraph(
                title,
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
                description,
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
    # WORKFLOW
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL SYNCHRONIZATION WORKFLOW",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    workflow_steps = [

    "Broker Connection Established",
    "↓",

    "Broker Verification Completed",
    "↓",

    "Synchronization Job Created",
    "↓",

    "Evidence Acquisition Initiated",
    "↓",

    "Synchronization Processing",
    "↓",

    "Canonical Evidence Generation",
    "↓",

    "Canonical Evidence Persistence",
    "↓",

    "Institutional Governance Enforcement",

    ]

    for step in workflow_steps:

        story.append(
            Paragraph(
                step,
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
            "SYNCHRONIZATION GOVERNANCE",
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
            "Every synchronization job performed "
            "by Trading Truth Layer is "
            "institutionally governed.",
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

        "Broker provenance.",

        "Synchronization timestamps.",

        "Evidence provenance.",

        "Trust tier assignments.",

        "Synchronization status.",

        "Canonical evidence mappings.",

        "Historical synchronization records.",

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

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INSTITUTIONAL QUESTIONS ANSWERED",
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

        "Has broker evidence been synchronized successfully?",

        "Which synchronization category was performed?",

        "Can synchronized evidence be trusted?",

        "Has broker provenance been preserved?",

        "Which trust tier has been assigned?",

        "Was canonical evidence successfully generated?",

        "Has institutional evidence successfully entered the TTL trust workflow?",

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

    workflow_position = [

        "Broker Connections",

        "↓",

        "Sync Center",

        "↓",

        "Canonical Evidence Infrastructure",

        "↓",

        "Claim Infrastructure",

        "↓",

        "Institutional Verification Workflow",

    ]

    for item in workflow_position:

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