"""
Trading Truth Layer

Institutional Positioning

This module formally establishes Trading Truth
Layer's institutional positioning as Institutional
Trading Trust Infrastructure for Evidence-Based
Capital Allocation.
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

from app.services.pdf.guidebooks.common.guidebook_constants import (
    TTL_POSITIONING_STATEMENT,
    TTL_MISSION_STATEMENT,
    TTL_VISION_STATEMENT,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_institutional_positioning():

    """
    Builds the Institutional Positioning page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL POSITIONING",
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
    # POSITIONING STATEMENT
    # --------------------------------------------------

    story.append(
        Paragraph(
            TTL_POSITIONING_STATEMENT,
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
    # INSTITUTIONAL NARRATIVE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer is not attempting "
            "to improve existing trading software. "
            "It is establishing a new institutional "
            "infrastructure category for global "
            "capital markets.",
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
            "Institutional Trading Trust Infrastructure "
            "represents the missing infrastructure layer "
            "required to independently establish trust "
            "in trading performance records.",
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
    # MISSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "MISSION",
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
            TTL_MISSION_STATEMENT,
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
    # VISION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VISION",
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
            TTL_VISION_STATEMENT,
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
    # INSTITUTIONAL CONCLUSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer exists to establish "
            "institutional trust infrastructure that "
            "enables evidence-based capital allocation "
            "across global capital markets.",
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