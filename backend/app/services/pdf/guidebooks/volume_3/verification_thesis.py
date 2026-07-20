"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

The Institutional Verification Thesis
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


def build_verification_thesis():

    """
    Builds the Institutional Verification
    Thesis section for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE INSTITUTIONAL VERIFICATION THESIS",
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
    # THE THESIS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading performance should not be "
            "treated as self-reported historical "
            "performance data.",
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
            "Trading performance should be treated "
            "as independently verifiable "
            "institutional evidence capable of "
            "supporting institutional capital "
            "allocation decisions.",
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
    # INSTITUTIONAL REQUIREMENTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Independent trading verification "
            "requires institutional infrastructure "
            "capable of establishing:",
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

        "Evidence authenticity.",

        "Trade provenance.",

        "Data integrity.",

        "Institutional governance.",

        "Independent verification standards.",

        "Allocator-ready institutional outputs.",

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
    # TTL POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional trading verification "
            "exists to transform trading activity "
            "into independently verifiable "
            "institutional evidence.",
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
            "Independent verification is the "
            "foundation of evidence-based "
            "capital allocation.",
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