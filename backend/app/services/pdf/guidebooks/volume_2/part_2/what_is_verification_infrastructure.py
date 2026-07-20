"""
Trading Truth Layer

What Is Verification Infrastructure?

This module introduces Verification
Infrastructure as an institutional
capability required to independently
verify trading performance records.
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


def build_what_is_verification_infrastructure():

    """
    Builds the What Is Verification
    Infrastructure page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHAT IS VERIFICATION INFRASTRUCTURE?",
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
    # INSTITUTIONAL DEFINITION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Verification Infrastructure is the "
            "institutional capability responsible "
            "for independently establishing trust "
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
            "Its responsibility is not to measure "
            "performance. Its responsibility is to "
            "determine whether trading performance "
            "can be independently verified.",
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
            "Verification Infrastructure operates "
            "upstream of institutional due diligence, "
            "capital allocation, investigations, and "
            "public trust systems.",
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
    # RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Verification Infrastructure is "
            "responsible for:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    responsibilities = [

        "Evidence ingestion.",
        "Evidence normalization.",
        "Canonical trade ledger creation.",
        "Institutional verification.",
        "Integrity monitoring.",
        "Governance procedures.",
        "Verification workflows.",
        "Institutional reporting.",
        "Trust intelligence generation.",

    ]

    for responsibility in responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
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

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Verification Infrastructure transforms "
            "trading activity into institutional "
            "evidence capable of supporting "
            "institutional trust.",
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
            "Institutional verification should not "
            "depend upon assumptions. It should "
            "depend upon infrastructure.",
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