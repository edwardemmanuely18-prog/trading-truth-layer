"""
Trading Truth Layer

From Performance to Trust

This module introduces the philosophical
evolution from trading performance to
institutional trust infrastructure.
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


def build_from_performance_to_trust():

    """
    Builds the From Performance to Trust page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "FROM PERFORMANCE TO TRUST",
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
            "Historically, trading performance has "
            "been treated as historical data, "
            "performance statistics, broker statements, "
            "and analytical records.",
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
            "Trading Truth Layer challenges this "
            "fundamental assumption.",
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
            "Trading performance is not merely "
            "historical data.",
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
            "Trading performance is institutional "
            "evidence.",
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
            "Institutional evidence requires "
            "institutional trust.",
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
            "Institutional trust requires "
            "institutional infrastructure.",
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
            "The evolution from performance to trust "
            "fundamentally changes how global capital "
            "markets evaluate trading records.",
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
            "Trading Truth Layer was established "
            "to enable this institutional transition.",
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