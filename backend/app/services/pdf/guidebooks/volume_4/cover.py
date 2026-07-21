"""
Trading Truth Layer

Volume IV

Trading Truth Layer Institutional Domains

Cover Page
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


def build_cover():

    """
    Builds the institutional cover page
    for Volume IV.
    """

    story = []

    # --------------------------------------------------
    # TITLE
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
            SPACE_LG,
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
    # INSTITUTIONAL QUESTIONS
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

    institutional_questions = [

        "Which institutional domains compose Trading Truth Layer?",

        "What institutional responsibilities belong to each domain?",

        "How do institutional domains interact with one another?",

        "How does institutional trust flow throughout the TTL ecosystem?",

        "How does Trading Truth Layer transform trading activity into institutional intelligence?",

        "How is institutional trust governed across the ecosystem?",

    ]

    for question in institutional_questions:

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
    # INSTITUTIONAL THESIS
    # --------------------------------------------------

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

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