"""
Trading Truth Layer

What is Trading Truth Layer?

This module formally defines Trading Truth Layer
as Institutional Trading Trust Infrastructure for
Evidence-Based Capital Allocation.
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
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_what_is_ttl():

    """
    Builds the What is Trading Truth Layer page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHAT IS TRADING TRUTH LAYER?",
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
    # WHAT TTL IS NOT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer is not a trading "
            "journal, broker, portfolio tracker, "
            "social trading platform, or trading "
            "analytics application.",
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
            "It is not another tool designed to "
            "visualize trading performance.",
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
    # WHAT TTL IS
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

    story.append(
        Paragraph(
            "Trading Truth Layer establishes an "
            "institutional infrastructure layer "
            "designed to independently establish "
            "trust in trading performance records.",
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
            "Its purpose is to transform trading "
            "performance into institutional evidence "
            "capable of supporting evidence-based "
            "capital allocation.",
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
            "Trading Truth Layer represents a new "
            "institutional infrastructure category "
            "within global capital markets.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    story.append(
        Paragraph(
            "Institutional trust should be "
            "infrastructure.",
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