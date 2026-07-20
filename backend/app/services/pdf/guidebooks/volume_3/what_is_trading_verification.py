"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

What is Trading Verification?
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


def build_what_is_trading_verification():

    """
    Builds the What is Trading Verification?
    section for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHAT IS TRADING VERIFICATION?",
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
    # DEFINITION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Verification is the "
            "institutional process of determining "
            "whether trading activity and its "
            "associated performance records can "
            "be independently trusted.",
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
            "Institutional trading verification "
            "extends beyond the review of "
            "historical performance metrics and "
            "requires the evaluation of the "
            "underlying trading evidence itself.",
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
    # INSTITUTIONAL OBJECTIVES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Verification Infrastructure "
            "exists to establish:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    objectives = [

        "The authenticity of trading activity.",

        "The integrity of trading records.",

        "The provenance of trading evidence.",

        "The trustworthiness of trading performance.",

        "The institutional readiness of trading records.",

        "The allocator readiness of institutional evidence.",

    ]

    for objective in objectives:

        story.append(
            Paragraph(
                f"• {objective}",
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
            "Trading Verification Infrastructure "
            "exists to determine whether trading "
            "performance can be independently "
            "trusted before institutional capital "
            "is allocated.",
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
            "Institutional trading verification "
            "is the foundation of independently "
            "verifiable trading performance.",
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