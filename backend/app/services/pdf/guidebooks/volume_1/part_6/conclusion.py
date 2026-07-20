"""
Trading Truth Layer

Conclusion

This module renders the institutional
closing statement for Volume I of the
Trading Truth Layer Guidebook Series.
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

from app.services.pdf.guidebooks.common.guidebook_constants import (
    TTL_POSITIONING_STATEMENT,
    FUTURE_OF_TRUST_STATEMENT,
    FUTURE_OF_CAPITAL_ALLOCATION_STATEMENT,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_conclusion():

    """
    Builds the institutional conclusion page
    for Volume I.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
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
    # INSTITUTIONAL DECLARATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional Trading Trust Infrastructure "
            "is not an optional capability of modern "
            "capital markets. It is an inevitable "
            "institutional requirement.",
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
            "Trading performance is institutional "
            "evidence that deserves institutional trust.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(

        Paragraph(
            "The future of global capital allocation "
            "will not be determined solely by trading "
            "performance. It will be determined by the "
            "institutional quality of the trust "
            "infrastructure supporting that performance.",
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
            "Evidence-based capital allocation begins "
            "with evidence-based trust.",
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
    # FUTURE STATEMENTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            FUTURE_OF_TRUST_STATEMENT,
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
            FUTURE_OF_CAPITAL_ALLOCATION_STATEMENT,
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
            "Institutional trust infrastructure enables "
            "capital allocators to make evidence-based "
            "decisions with confidence, transparency, "
            "and independently verifiable records.",
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
    # INSTITUTIONAL CLOSING STATEMENT
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