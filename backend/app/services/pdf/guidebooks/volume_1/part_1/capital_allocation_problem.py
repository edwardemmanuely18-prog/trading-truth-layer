"""
Trading Truth Layer

The Capital Allocation Problem

This module introduces the institutional
capital allocation problems that exist
throughout global capital markets today.
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


def build_capital_allocation_problem():

    """
    Builds the Capital Allocation Problem page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE CAPITAL ALLOCATION PROBLEM",
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
    # INSTITUTIONAL NARRATIVE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional capital is not allocated "
            "based upon claims. It is allocated "
            "based upon trust.",
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
            "Before capital can be allocated, "
            "institutions must independently "
            "determine whether the underlying "
            "trading activity can be trusted.",
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
            "Yet global trading infrastructure "
            "was never designed to produce "
            "allocator-ready trust records.",
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
            "Institutional allocators require "
            "evidence, governance, transparency, "
            "and independently verifiable records "
            "before capital can be deployed.",
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
            "Capital allocation is fundamentally "
            "an institutional trust problem.",
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
            "Without trust, institutional capital "
            "cannot scale.",
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
            "Evidence-based capital allocation "
            "requires institutional trust infrastructure.",
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