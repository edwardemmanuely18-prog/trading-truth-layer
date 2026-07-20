"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

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
    for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TRADING VERIFICATION "
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
            "Institutional Infrastructure for "
            "Independent Trading Performance "
            "Verification",
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
    # THE PROBLEM
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading performance is one of the "
            "most valuable forms of financial "
            "information within global capital "
            "markets.",
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
            "Despite the growth of modern trading "
            "technology, there remains no "
            "institutional standard for "
            "independently verifying whether "
            "a trading performance record can "
            "be trusted.",
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
    # TTL POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer is building the "
            "Trading Verification Infrastructure "
            "required to transform trading "
            "activity into evidence-backed and "
            "institutionally verifiable "
            "performance records.",
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
            "Independent trading verification "
            "is a prerequisite for evidence-based "
            "capital allocation.",
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