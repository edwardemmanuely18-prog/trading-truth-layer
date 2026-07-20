"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

Verification Bands
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


def build_verification_bands():

    """
    Builds the Verification Bands section
    for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION BANDS",
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
            "Institutional trust is not binary.",
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
            "Trading records may exhibit varying "
            "levels of institutional trust, "
            "verification coverage and allocator "
            "readiness.",
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
            "Trading Truth Layer utilizes "
            "Verification Bands to communicate "
            "the institutional verification "
            "posture of a trading record.",
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
    # PURPOSE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL PURPOSE",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    purposes = [

        "Communicate institutional trust levels.",

        "Communicate verification readiness.",

        "Communicate allocator readiness.",

        "Communicate verification outcomes.",

        "Communicate institutional confidence.",

        "Communicate institutional review findings.",

    ]

    for purpose in purposes:

        story.append(
            Paragraph(
                f"• {purpose}",
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
    # INSTITUTIONAL INTERPRETATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL INTERPRETATION",
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
            "Verification Bands provide "
            "institutions with an immediately "
            "understandable representation of "
            "the verification posture of a "
            "trading record.",
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
            "Rather than evaluating individual "
            "metrics in isolation, institutions "
            "may utilize Verification Bands as "
            "a consolidated institutional trust "
            "indicator.",
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
    # QUESTIONS ANSWERED
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INSTITUTIONAL QUESTIONS ANSWERED",
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

        "What is the verification posture of the record?",

        "Can the record be institutionally trusted?",

        "Can the record support allocator review?",

        "Has institutional verification been completed?",

        "Can institutions rely upon the verification outcome?",

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
            "Verification Bands provide a "
            "standardized institutional language "
            "for communicating verification "
            "outcomes.",
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
            "Institutional trust should be "
            "communicated clearly, consistently "
            "and independently.",
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