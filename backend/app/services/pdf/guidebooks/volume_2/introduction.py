"""
Trading Truth Layer

Volume II

Verification Infrastructure

This module introduces the institutional
verification infrastructure required to
transform trading performance into
independently verifiable institutional
evidence.
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
    SPACE_SM,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_introduction():

    """
    Builds the introduction page for
    Volume II - Verification Infrastructure.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
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
    # INSTITUTIONAL INTRODUCTION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional trust cannot exist "
            "without institutional verification.",
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
            "Before institutions can rely upon "
            "trading performance records, they "
            "must be able to independently verify "
            "the underlying evidence.",
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
            "Verification is the process that "
            "transforms trading activity into "
            "institutionally reviewable and "
            "allocator-ready evidence.",
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
            "Modern trading infrastructure was "
            "designed to execute trades and "
            "report performance. It was not "
            "designed to independently verify "
            "trading records for institutional "
            "capital allocation.",
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
    # VOLUME II OBJECTIVE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Volume II introduces the verification "
            "infrastructure layer of Trading Truth "
            "Layer.",
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
            "This volume explains how Trading Truth "
            "Layer performs evidence ingestion, "
            "claim verification, integrity analysis, "
            "governance procedures, and institutional "
            "verification workflows.",
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
            "The objective of this guidebook is to "
            "demonstrate how institutional verification "
            "infrastructure enables independently "
            "verifiable trading performance across "
            "global capital markets.",
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
    # POSITIONING STATEMENT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Verification is the foundation of "
            "institutional trust.",
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