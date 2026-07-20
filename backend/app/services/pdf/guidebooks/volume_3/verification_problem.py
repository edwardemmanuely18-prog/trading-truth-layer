"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

The Trading Verification Problem
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


def build_verification_problem():

    """
    Builds the Trading Verification
    Problem section for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE TRADING VERIFICATION PROBLEM",
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
    # GLOBAL PROBLEM
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Global capital markets currently "
            "lack an institutional standard for "
            "determining whether trading "
            "performance records can be "
            "independently verified.",
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
            "Trading performance is routinely "
            "represented through screenshots, "
            "broker statements, spreadsheets and "
            "historical summaries that provide "
            "little insight into the authenticity "
            "of the underlying trading activity.",
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
    # INSTITUTIONAL LIMITATIONS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutions are therefore unable to "
            "answer fundamental verification "
            "questions before allocating capital.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    verification_questions = [

        "Did the trading activity actually occur?",

        "Can the evidence be independently verified?",

        "Has the trading record been altered?",

        "Can the performance record survive institutional review?",

    ]

    for question in verification_questions:

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
            "Institutional capital allocation "
            "requires institutional trading "
            "verification.",
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