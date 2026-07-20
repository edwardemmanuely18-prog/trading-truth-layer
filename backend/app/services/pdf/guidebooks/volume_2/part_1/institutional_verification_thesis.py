"""
Trading Truth Layer

Institutional Verification Thesis

This module formally establishes the
institutional thesis behind Verification
Infrastructure.

Institutional Verification Infrastructure
exists to transform trading performance
into independently verifiable institutional
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
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_institutional_verification_thesis():

    """
    Builds the Institutional Verification
    Thesis page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
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
    # INSTITUTIONAL DECLARATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading performance should not merely "
            "be reported.",
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
            "Trading performance should be "
            "independently verifiable.",
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
    # INSTITUTIONAL THESIS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional verification infrastructure "
            "exists to establish institutional confidence "
            "in trading evidence.",
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
            "Verification is the process through which "
            "trading activity is transformed into "
            "machine-readable, independently verifiable, "
            "institutional records.",
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
            "Institutional capital cannot rely upon "
            "claims. It relies upon evidence that "
            "can withstand independent verification.",
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
    # TTL POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer is being built to "
            "provide institutional verification "
            "infrastructure for trading performance.",
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
            "Verification is not a feature.",
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
            "Verification is infrastructure.",
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
    # CONCLUSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional trust emerges when "
            "verification is embedded into the "
            "underlying infrastructure of global "
            "capital markets.",
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