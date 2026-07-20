"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

Institutional Verification Standards
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


def build_institutional_standards():

    """
    Builds the Institutional Verification
    Standards section for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL VERIFICATION STANDARDS",
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
            "Institutional trust should never be "
            "assumed. It must be independently "
            "established through governed "
            "verification standards.",
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
            "Trading Truth Layer establishes "
            "institutional standards designed "
            "to determine whether trading "
            "records are capable of supporting "
            "institutional trust and evidence-"
            "based capital allocation.",
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
    # STANDARDS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL VERIFICATION STANDARDS",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    standards = [

        "Evidence provenance must be preserved.",

        "Trading records must originate from governed evidence sources.",

        "Institutional trust tiers must be assigned.",

        "Trading evidence must be independently verifiable.",

        "Historical synchronization records must exist.",

        "Institutional governance requirements must be satisfied.",

        "Verification workflows must successfully complete.",

        "Canonical institutional records must be established.",

    ]

    for standard in standards:

        story.append(
            Paragraph(
                f"• {standard}",
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
    # CAPITAL ALLOCATION STANDARDS
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INSTITUTIONAL CAPITAL ALLOCATION STANDARDS",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    allocation_standards = [

        "Allocator-ready institutional evidence.",

        "Audit-ready verification records.",

        "Dispute-ready evidence packages.",

        "Institutional governance records.",

        "Machine-readable institutional outputs.",

        "Canonical institutional trust records.",

    ]

    for standard in allocation_standards:

        story.append(
            Paragraph(
                f"• {standard}",
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
    # INSTITUTIONAL REQUIREMENTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL REQUIREMENTS",
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
            "Trading performance should not be "
            "evaluated solely by profitability "
            "metrics. Institutional trust "
            "requires governed evidence, "
            "institutional verification and "
            "institutional accountability.",
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
            "Institutional verification therefore "
            "evaluates the trustworthiness of "
            "trading records rather than merely "
            "evaluating historical profitability.",
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

        "Can the trading evidence be trusted?",

        "Were institutional verification standards satisfied?",

        "Can institutional capital rely upon the trading records?",

        "Are the records allocator-ready?",

        "Can the evidence support institutional due diligence?",

        "Can the records be independently verified?",

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
            "Institutional trust is the product "
            "of governed verification standards "
            "rather than historical performance "
            "claims.",
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
            "Institutional verification standards "
            "exist to protect institutional capital "
            "through independently verifiable "
            "trading evidence.",
            BODY_CENTER_STYLE,
        )
    )


    return story


# ==========================================================
# END OF FILE
# ==========================================================