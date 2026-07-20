"""
Trading Truth Layer

The Four Institutional Questions

This page introduces the four canonical
institutional questions that define the
Trading Truth Layer ecosystem.

Every infrastructure component inside TTL
ultimately exists to answer these questions.
"""

from reportlab.platypus import (
    Paragraph,
    Spacer,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    SUBTITLE_STYLE,
    BODY_STYLE,
    BODY_CENTER_STYLE,
    SPACE_SM,
    SPACE_MD,
    SPACE_LG,
)

from app.services.pdf.guidebooks.common.guidebook_constants import (
    TTL_FOUR_QUESTIONS,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_four_questions():
    """
    Builds the canonical Four Questions page
    for Volume I.

    Returns
    -------
    list

        ReportLab flowables representing
        the complete Four Questions page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE FOUR QUESTIONS<br/>"
            "TRADING TRUTH LAYER ANSWERS",
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
    # INTRODUCTION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Every infrastructure component inside "
            "Trading Truth Layer ultimately exists "
            "to answer four institutional questions.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    QUESTIONS = [

        (
            "QUESTION I",
            TTL_FOUR_QUESTIONS[0],
            "Institutional trust begins with the ability "
            "to independently verify trading performance."
        ),

        (
            "QUESTION II",
            TTL_FOUR_QUESTIONS[1],
            "Evidence-based capital allocation requires "
            "institutional confidence in the underlying records."
        ),

        (
            "QUESTION III",
            TTL_FOUR_QUESTIONS[2],
            "Institutional due diligence requires independently "
            "verifiable evidence and governance."
        ),

        (
            "QUESTION IV",
            TTL_FOUR_QUESTIONS[3],
            "Global capital markets require institutional "
            "trust infrastructure capable of operating at scale."
        ),

    ]


    for title, question, explanation in QUESTIONS:

        story.append(
            Paragraph(
                title,
                SUBTITLE_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                4,
            )
        )

        story.append(
            Paragraph(
                question,
                BODY_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                4,
            )
        )

        story.append(
            Paragraph(
                explanation,
                BODY_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                6,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_SM,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL CONCLUSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "If any of these four questions cannot "
            "be answered with institutional confidence, "
            "trust cannot exist.",
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
            "Without trust, institutional capital "
            "cannot scale.",
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
            "Trading Truth Layer exists to establish "
            "the institutional trust infrastructure "
            "required to answer these questions "
            "through evidence-based trust.",
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