"""
Trading Truth Layer

Part I

The Trust Problem

This module renders the institutional
separator page for Part I of Volume I.
"""

from reportlab.platypus import (
    Paragraph,
    Spacer,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    BODY_CENTER_STYLE,
    SPACE_MD,
    SPACE_SM,
)

from app.services.pdf.guidebooks.common.guidebook_constants import (
    PART_1_TITLE,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_part_1():

    """
    Builds the institutional separator page
    for Part I - The Trust Problem.
    """

    story = []

    # --------------------------------------------------
    # PART TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PART I",
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
            PART_1_TITLE,
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL NARRATIVE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trust is one of the most fundamental "
            "requirements of institutional capital "
            "allocation.",
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
            "Every institutional investment decision "
            "ultimately depends upon the ability to "
            "independently establish trust in the "
            "underlying evidence.",
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
            "Unfortunately, modern trading "
            "infrastructure was never designed "
            "to establish institutional trust "
            "in trading performance.",
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
            "Part I examines the institutional trust "
            "problems that exist throughout global "
            "capital markets today.",
            BODY_CENTER_STYLE,
        )
    )

    return story


# ==========================================================
# END OF FILE
# ==========================================================