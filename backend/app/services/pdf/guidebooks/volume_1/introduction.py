"""
Trading Truth Layer

Introduction

This page formally introduces Trading Truth Layer
as Institutional Trading Trust Infrastructure for
Evidence-Based Capital Allocation.

The purpose of this page is not to explain how
Trading Truth Layer works.

The purpose of this page is to establish the
institutional problem category that Trading Truth
Layer exists to solve.
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

from app.services.pdf.guidebooks.common.guidebook_constants import (
    TTL_POSITIONING_STATEMENT,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_introduction():
    """
    Builds the institutional introduction page
    for Volume I.

    Returns
    -------
    list

        ReportLab flowables representing
        the complete Introduction page.
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
    # INTRODUCTION NARRATIVE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Modern financial markets have "
            "successfully built institutional "
            "infrastructure for market data, "
            "payments, cloud computing, software "
            "collaboration, financial reporting, "
            "compliance, and trade execution.",
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
            "Yet one institutional infrastructure "
            "layer remains conspicuously absent "
            "from global capital markets.",
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
            "Institutional Trading Trust Infrastructure.",
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
    # POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            TTL_POSITIONING_STATEMENT,
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
    # INSTITUTIONAL CONTEXT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer was not created "
            "to solve a trading performance problem. "
            "It was created to solve an institutional "
            "trust infrastructure problem.",
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
            "Trading performance continues to be "
            "communicated through screenshots, "
            "spreadsheets, broker statements, and "
            "third-party analytics despite the "
            "fact that billions of dollars are "
            "allocated based upon these records.",
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
            "Trading Truth Layer exists because "
            "institutional capital deserves "
            "institutional trust.",
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
            "The future of trading performance "
            "is trust.",
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