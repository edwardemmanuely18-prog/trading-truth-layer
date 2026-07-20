"""
Trading Truth Layer

The Missing Institutional Infrastructure

This module formally introduces the missing
institutional infrastructure layer that
Trading Truth Layer exists to establish.

Institutional Trading Trust Infrastructure
for Evidence-Based Capital Allocation.
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


def build_missing_institutional_infrastructure():

    """
    Builds the institutional infrastructure
    declaration page for Volume I.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE MISSING INSTITUTIONAL "
            "INFRASTRUCTURE",
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
            "Institutional Trust Infrastructure<br/>"
            "for Evidence-Based Capital Allocation",
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
    # INFRASTRUCTURE ANALOGIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "&#8226; There is Bloomberg for market data.",
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
            "&#8226; There is Stripe for payments.",
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
            "&#8226; There is GitHub for software collaboration.",
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
    # MISSING INFRASTRUCTURE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "&#8226; There is still no institutional trust "
            "infrastructure for trading performance.",
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
    # TTL POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "&#8226; Trading Truth Layer is being built "
            "to become that infrastructure.",
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
            "&#8226; Institutional trust should be infrastructure.",
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