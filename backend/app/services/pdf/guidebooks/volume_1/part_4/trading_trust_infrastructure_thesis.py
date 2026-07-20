"""
Trading Truth Layer

The Trading Trust Infrastructure Thesis

This module formally establishes the
institutional thesis upon which Trading Truth
Layer is built.
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


def build_trading_trust_infrastructure_thesis():

    """
    Builds the Trading Trust Infrastructure Thesis page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE TRADING TRUST INFRASTRUCTURE THESIS",
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
    # INSTITUTIONAL THESIS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Modern capital markets cannot function "
            "without institutional trust.",
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
            "Institutional trust depends upon "
            "institutional evidence.",
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
            "Institutional evidence depends upon "
            "institutional infrastructure.",
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
    # INFRASTRUCTURE THESIS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Global capital markets have established "
            "institutional infrastructure for nearly "
            "every critical financial function except "
            "institutional trust in trading performance.",
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
            "The absence of Institutional Trading Trust "
            "Infrastructure explains the trust, capital "
            "allocation, and due diligence problems "
            "that exist today.",
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
    # CAPITAL ALLOCATION THESIS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Evidence-based capital allocation cannot "
            "exist without evidence-based trust.",
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
            "Evidence-based trust cannot exist without "
            "institutional trust infrastructure.",
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
            "Institutional Trading Trust Infrastructure "
            "is not optional. It is inevitable.",
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
    # INSTITUTIONAL CONCLUSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer exists to establish "
            "the institutional trust infrastructure "
            "required for evidence-based capital "
            "allocation across global capital markets.",
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