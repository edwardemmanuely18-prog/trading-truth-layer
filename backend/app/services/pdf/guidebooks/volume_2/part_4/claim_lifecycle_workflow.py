"""
Trading Truth Layer

Claim Lifecycle Workflow

This module formally introduces the
institutional lifecycle workflow of
trading claims throughout Trading
Truth Layer's Verification Infrastructure.

Every trading claim progresses through
a governed institutional lifecycle.
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
    SPACE_SM,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_claim_lifecycle_workflow():

    """
    Builds the Claim Lifecycle Workflow page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE CLAIM LIFECYCLE WORKFLOW",
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
            "Institutional evidence must be "
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

    story.append(
        Paragraph(
            "Trading Truth Layer implements a "
            "governed lifecycle workflow for "
            "every institutional trading claim.",
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
            "The lifecycle workflow ensures that "
            "verification procedures, governance "
            "controls and historical auditability "
            "are preserved throughout the existence "
            "of every claim.",
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
    # LIFECYCLE STATES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Every institutional trading claim "
            "progresses through four lifecycle states:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    lifecycle_states = [

        "Draft",

        "Verify",

        "Publish",

        "Lock",

    ]

    for state in lifecycle_states:

        story.append(
            Paragraph(
                f"• {state}",
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_SM,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # GOVERNANCE OBJECTIVES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The institutional lifecycle workflow "
            "exists to preserve:",
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

        "Verification integrity.",

        "Historical auditability.",

        "Governance compliance.",

        "Institutional transparency.",

        "Claim immutability.",

        "Evidence provenance.",

        "Allocator confidence.",

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
                SPACE_SM,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading claims are not static "
            "performance reports.",
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
            "They are governed institutional "
            "records that evolve through "
            "verification and publication "
            "workflows before becoming "
            "institutionally locked evidence.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_SM,
        )
    )

    story.append(
        Paragraph(
            "Institutional trust begins when "
            "institutional governance is enforced.",
            BODY_CENTER_STYLE,
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