"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

Introduction
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


def build_introduction():

    """
    Builds the introduction section
    for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INTRODUCTION",
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
    # INSTITUTIONAL PROBLEM
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional capital cannot rely "
            "upon unverified trading performance "
            "records.",
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
            "Before institutions allocate capital, "
            "they must determine whether the "
            "underlying trading activity can be "
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

    # --------------------------------------------------
    # TTL POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer is being built "
            "to establish institutional trading "
            "verification standards capable of "
            "transforming trading activity into "
            "independently verifiable institutional "
            "records.",
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
    # WHAT THIS VOLUME INTRODUCES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Volume III introduces the trading "
            "verification infrastructure, "
            "verification standards, broker "
            "synchronization mechanisms, "
            "verification workflows and "
            "institutional outputs required to "
            "perform evidence-based trading "
            "verification.",
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
    # POSITIONING STATEMENT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional trust begins with "
            "institutional verification.",
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