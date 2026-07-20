"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

Next Volume
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


def build_next_volume():

    """
    Builds the Next Volume section
    for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "NEXT VOLUME",
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
            "Independent verification establishes "
            "institutional trust. The next "
            "institutional question is where "
            "that trust is established throughout "
            "the Trading Truth Layer ecosystem.",
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
            "Institutional trust does not exist "
            "within a single component. It is "
            "established across multiple "
            "institutional domains operating "
            "together to transform trading "
            "activity into allocator-ready "
            "institutional intelligence.",
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
    # VOLUME IV
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VOLUME IV",
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
            "TRADING TRUTH LAYER "
            "INSTITUTIONAL DOMAINS",
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
    # QUESTIONS TO BE ANSWERED
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Volume IV answers the following "
            "institutional questions:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    questions = [

        "What institutional domains compose Trading Truth Layer?",

        "What institutional responsibilities belong to each domain?",

        "How does institutional trust flow across the TTL ecosystem?",

        "How do institutional domains interact with one another?",

        "How does TTL transform trading activity into institutional intelligence?",

        "How is institutional trust governed across the ecosystem?",

    ]

    for question in questions:

        story.append(
            Paragraph(
                f"• {question}",
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_MD,
            )
        )

    # --------------------------------------------------
    # POSITIONING STATEMENT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional trust is not produced "
            "by a single verification process. "
            "It is produced by an institutional "
            "ecosystem.",
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
            "Volume IV formally introduces the "
            "institutional domains responsible "
            "for establishing trust throughout "
            "Trading Truth Layer.",
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