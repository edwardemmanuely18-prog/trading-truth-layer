"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

The Future of Trading Verification
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


def build_future_of_trading_verification():

    """
    Builds the Future of Trading
    Verification section for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE FUTURE OF TRADING VERIFICATION",
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
            "Institutional capital is becoming "
            "increasingly dependent upon trusted "
            "financial information.",
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
            "As capital markets become more "
            "global, automated and evidence-driven, "
            "the demand for independently "
            "verifiable trading records will "
            "continue to increase.",
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
    # FUTURE REQUIREMENTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "FUTURE INSTITUTIONAL REQUIREMENTS",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    requirements = [

        "Independent trading verification.",

        "Institutional trust infrastructure.",

        "Allocator-ready trust artifacts.",

        "Machine-readable institutional evidence.",

        "Global verification standards.",

        "Evidence-based capital allocation.",

    ]

    for requirement in requirements:

        story.append(
            Paragraph(
                f"• {requirement}",
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
    # TTL VISION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer envisions a "
            "future in which institutional "
            "verification becomes a standard "
            "requirement of global capital "
            "allocation.",
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
            "Trading performance should be "
            "institutionally verified before "
            "institutions allocate capital, "
            "conduct due diligence or make "
            "investment decisions.",
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
    # INSTITUTIONAL QUESTIONS
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

        "Will institutional verification become a market standard?",

        "Can institutional trust be standardized globally?",

        "Will allocators require independently verified records?",

        "Can capital allocation become evidence based?",

        "What role will verification infrastructure play in the future?",

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
            "The future of institutional capital "
            "allocation is independently "
            "verifiable.",
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
            "will become a foundational component "
            "of global capital markets.",
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