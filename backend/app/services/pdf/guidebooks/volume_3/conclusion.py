"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

Conclusion
"""

from reportlab.platypus import (
    Paragraph,
    Spacer,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    BODY_CENTER_STYLE,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_conclusion():

    """
    Builds the Conclusion section
    for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CONCLUSION",
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
    # THE JOURNEY CONTINUES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE JOURNEY CONTINUES",
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
    # FUTURE OF TRADING VERIFICATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE FUTURE OF",
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
            "TRADING VERIFICATION",
            BODY_CENTER_STYLE,
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
            "Institutional Trading Verification",
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
    # INSTITUTIONAL QUESTION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL QUESTION",
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
            "Can global capital markets adopt "
            "independent trading verification "
            "standards?",
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
    # THE FUTURE EXPLORES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE FUTURE EXPLORES:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    future_topics = [

        "Global Verification Standards",

        "Institutional Trust Infrastructure",

        "Evidence Based Capital Allocation",

        "Allocator Ready Verification",

        "Independent Trading Verification",

        "The Trading Truth Network",

    ]

    for topic in future_topics:

        story.append(
            Paragraph(
                topic,
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
    # GUIDEBOOK SERIES
    # --------------------------------------------------

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    story.append(
        Paragraph(
            "Trading Truth Layer Guidebook Series",
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
