"""
Trading Truth Layer

The Five Institutional Problems

This module introduces the five institutional
problems that Trading Truth Layer exists to
address through Institutional Trading Trust
Infrastructure.
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
    SPACE_SM,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_five_problems_ttl_addresses():

    """
    Builds the Five Institutional Problems page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE FIVE INSTITUTIONAL PROBLEMS",
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
            "Trading Truth Layer was created to "
            "address five institutional problems "
            "that currently exist throughout global "
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

    # --------------------------------------------------
    # FIVE PROBLEMS
    # --------------------------------------------------

    problems = [

        (
            "Problem I",
            "The Trading Trust Problem",
        ),

        (
            "Problem II",
            "The Capital Allocation Problem",
        ),

        (
            "Problem III",
            "The Institutional Due Diligence Problem",
        ),

        (
            "Problem IV",
            "The Institutional Transparency Problem",
        ),

        (
            "Problem V",
            "The Institutional Trust Infrastructure Problem",
        ),

    ]

    for title, problem in problems:

        story.append(

            Paragraph(
                title,
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
                problem,
                BODY_CENTER_STYLE,
            )

        )

        story.append(
            Spacer(
                1,
                SPACE_SM,
            )
        )

    # --------------------------------------------------
    # INSTITUTIONAL CONTEXT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Each of these institutional problems "
            "represents a missing capability within "
            "modern trading infrastructure.",
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
            "Trading Truth Layer establishes "
            "Institutional Trading Trust "
            "Infrastructure to enable evidence-based "
            "trust across global capital markets.",
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
            "Institutional trust is not a feature. "
            "It is infrastructure.",
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