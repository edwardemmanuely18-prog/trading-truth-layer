"""
Trading Truth Layer

Verification Workflow

This module formally introduces the
institutional verification workflow
implemented throughout Trading Truth
Layer's Verification Infrastructure.

The verification workflow defines how
trading activity becomes institutionally
verified evidence.
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


def build_verification_workflow():

    """
    Builds the Verification Workflow page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE VERIFICATION WORKFLOW",
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
            "Institutional verification is not "
            "a single operation.",
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
            "Verification is an institutional "
            "workflow that transforms trading "
            "activity into independently "
            "verifiable evidence.",
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
            "Every stage of the workflow is "
            "responsible for establishing "
            "institutional confidence in the "
            "underlying trading record.",
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
    # WORKFLOW STAGES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The institutional verification "
            "workflow consists of the following "
            "stages:",
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

        "Trading Activity",

        "Evidence Ingestion",

        "Canonical Trade Ledger",

        "Trading Verification",

        "Integrity Assessment",

        "Governance Review",

        "Institutional Verification",

    ]

    for stage in workflow:

        story.append(
            Paragraph(
                f"• {stage}",
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
    # INSTITUTIONAL OBJECTIVE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Each stage contributes to the "
            "institutional trustworthiness of "
            "the final trading record.",
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
            "Verification infrastructure must "
            "be repeatable, governed, and "
            "independently reviewable.",
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
    # POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer does not merely "
            "verify trading records.",
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
            "It governs the institutional "
            "workflow required to establish "
            "evidence-based trust.",
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