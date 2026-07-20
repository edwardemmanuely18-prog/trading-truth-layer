"""
Trading Truth Layer

The Institutional Realization

This module formalizes the central thesis of
Volume I of the Trading Truth Layer Guidebook
Series.

The global trading industry does not have a
performance problem.

It has a trust infrastructure problem.
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


def build_institutional_realization():

    """
    Builds the institutional realization page
    for Volume I.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE INSTITUTIONAL REALIZATION",
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
    # INSTITUTIONAL CONTEXT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "After examining the institutional "
            "problems facing modern capital markets, "
            "one conclusion becomes unavoidable.",
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
    # CENTRAL THESIS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The trading industry does not have "
            "a performance problem.",
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
            "It has a trust infrastructure problem.",
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
    # INSTITUTIONAL POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Modern trading infrastructure has "
            "successfully optimized execution, "
            "analytics, reporting and portfolio "
            "management capabilities.",
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
            "What remains missing is institutional "
            "trust infrastructure capable of "
            "independently establishing trust in "
            "trading performance.",
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
            "Institutional capital cannot allocate "
            "trust where institutional trust "
            "cannot be independently established.",
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