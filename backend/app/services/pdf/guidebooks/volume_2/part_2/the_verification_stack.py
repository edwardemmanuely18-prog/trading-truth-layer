"""
Trading Truth Layer

The Verification Stack

This module formally introduces the
institutional infrastructure layers that
collectively establish Trading Truth Layer's
Verification Infrastructure.
"""

from reportlab.platypus import (
    Paragraph,
    Spacer,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    SUBTITLE_STYLE,
    BODY_STYLE,
    BODY_CENTER_STYLE,
    SPACE_SM,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_the_verification_stack():

    """
    Builds the Verification Stack page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE VERIFICATION STACK",
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
            "Trading Truth Layer is composed of "
            "multiple institutional infrastructure "
            "layers that collectively transform "
            "trading activity into independently "
            "verifiable trading records.",
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
            "The Verification Stack establishes "
            "the institutional foundations required "
            "to support evidence-based verification.",
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
    # LAYER I
    # --------------------------------------------------

    story.append(
        Paragraph(
            "LAYER I - EVIDENCE INFRASTRUCTURE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_SM)
    )

    story.append(
        Paragraph(
            "Responsible for evidence intake, "
            "evidence normalization and canonical "
            "evidence storage.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    # --------------------------------------------------
    # LAYER II
    # --------------------------------------------------

    story.append(
        Paragraph(
            "LAYER II - VERIFICATION INFRASTRUCTURE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_SM)
    )

    story.append(
        Paragraph(
            "Responsible for claim lifecycle "
            "management, trading verification, "
            "trading performance intelligence "
            "and integrity monitoring.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    # --------------------------------------------------
    # LAYER III
    # --------------------------------------------------

    story.append(
        Paragraph(
            "LAYER III - TRUST INFRASTRUCTURE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_SM)
    )

    story.append(
        Paragraph(
            "Responsible for institutional "
            "investigations, trust intelligence, "
            "public trust systems and verification "
            "networks.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    # --------------------------------------------------
    # LAYER IV
    # --------------------------------------------------

    story.append(
        Paragraph(
            "LAYER IV - INSTITUTIONAL INFRASTRUCTURE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_SM)
    )

    story.append(
        Paragraph(
            "Responsible for institutional "
            "reporting, workspace governance, "
            "institutional due diligence and "
            "capital allocation workflows.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_LG)
    )

    # --------------------------------------------------
    # CONCLUSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Together, these infrastructure layers "
            "establish the institutional foundations "
            "required to independently verify trading "
            "performance records.",
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