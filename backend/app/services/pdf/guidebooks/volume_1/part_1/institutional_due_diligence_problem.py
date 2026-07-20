"""
Trading Truth Layer

The Institutional Due Diligence Problem

This module introduces the institutional
due diligence problems that exist throughout
global capital markets today.
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


def build_institutional_due_diligence_problem():

    """
    Builds the Institutional Due Diligence Problem page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE INSTITUTIONAL DUE DILIGENCE PROBLEM",
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
    # INSTITUTIONAL NARRATIVE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional due diligence begins with "
            "a simple question: can the underlying "
            "evidence be trusted?",
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
            "Institutional allocators, family offices, "
            "funds, and investment committees cannot "
            "allocate capital responsibly without "
            "independently establishing trust in the "
            "performance records presented to them.",
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
            "Yet modern trading infrastructure provides "
            "no institutional framework for conducting "
            "independent and evidence-based due diligence "
            "on trading performance.",
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
            "Institutional due diligence requires "
            "transparency, governance, provenance, "
            "and independently verifiable evidence.",
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
            "Without institutional trust infrastructure, "
            "institutional due diligence becomes a "
            "manual, fragmented, and often subjective "
            "process.",
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
    # INSTITUTIONAL CONCLUSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional due diligence is fundamentally "
            "an institutional trust problem.",
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
            "Trust cannot be assumed. It must be "
            "independently established.",
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
            "Trading Truth Layer exists because "
            "institutional due diligence deserves "
            "institutional trust infrastructure.",
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