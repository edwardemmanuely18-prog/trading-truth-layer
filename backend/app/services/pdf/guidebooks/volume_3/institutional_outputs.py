"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

Institutional Outputs
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


def build_institutional_outputs():

    """
    Builds the Institutional Outputs
    section for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL OUTPUTS",
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
            "Institutional verification should "
            "produce institutional outputs that "
            "can be consumed by allocators, "
            "auditors and institutional decision "
            "makers.",
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
            "Trading Truth Layer transforms "
            "institutional verification into "
            "governed trust artifacts capable of "
            "supporting evidence-based capital "
            "allocation.",
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
    # OUTPUTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL OUTPUTS",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    outputs = [

        "Verification Certificates.",

        "Verification Metrics.",

        "Verification Bands.",

        "Institutional Trust Records.",

        "Allocator-ready Verification Results.",

        "Institutional Trust Intelligence.",

    ]

    for output in outputs:

        story.append(
            Paragraph(
                f"• {output}",
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
    # INSTITUTIONAL VALUE
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INSTITUTIONAL VALUE",
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
            "Institutional outputs provide a "
            "standardized representation of "
            "institutional trust that may be "
            "consumed across the Trading Truth "
            "Layer ecosystem.",
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
            "These outputs establish a common "
            "institutional language for "
            "communicating verification outcomes "
            "across global capital markets.",
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
    # CONSUMERS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL CONSUMERS",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    consumers = [

        "Institutional Allocators.",

        "Investment Committees.",

        "Institutional Auditors.",

        "Institutional Review Teams.",

        "Trading Institutions.",

        "Capital Allocation Decision Makers.",

    ]

    for consumer in consumers:

        story.append(
            Paragraph(
                f"• {consumer}",
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
    # QUESTIONS ANSWERED
    # --------------------------------------------------

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

        "What institutional outputs were produced?",

        "Can the outputs support capital allocation decisions?",

        "Can institutions independently review the results?",

        "Can institutional trust be communicated consistently?",

        "Can allocators rely upon the verification outcome?",

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
            "Institutional verification should "
            "produce allocator-ready institutional "
            "trust artifacts.",
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
            "Institutional outputs transform "
            "verification results into evidence-"
            "based capital allocation intelligence.",
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