"""
Trading Truth Layer

Part II

The Missing Infrastructure

This module introduces the missing
institutional infrastructure layer that
Trading Truth Layer exists to establish.
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
    PART_2_TITLE,
    TTL_POSITIONING_STATEMENT,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_missing_infrastructure():

    """
    Builds Part II - The Missing Infrastructure.
    """

    story = []

    # --------------------------------------------------
    # PART TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PART II",
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
            PART_2_TITLE,
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
            "Global financial markets have invested "
            "decades building institutional "
            "infrastructure for market data, "
            "execution, compliance, payments, "
            "financial reporting, and portfolio "
            "management.",
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
            "Yet one institutional infrastructure "
            "layer remains absent.",
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
            "Institutional Trading Trust Infrastructure.",
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
            "The trust problems discussed throughout "
            "Part I are not independent problems. "
            "They are symptoms of a missing "
            "institutional infrastructure layer.",
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
            "Without institutional trust infrastructure, "
            "global capital markets cannot independently "
            "establish trust in trading performance "
            "records at institutional scale.",
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
            "Trading Truth Layer exists to establish "
            "the institutional trust infrastructure "
            "required for evidence-based capital "
            "allocation.",
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