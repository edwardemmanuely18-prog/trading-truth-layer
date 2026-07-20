"""
Trading Truth Layer

Verification Engine

This module formally introduces the
Verification Engine and its institutional
responsibility within Trading Truth Layer's
Verification Infrastructure.

The Verification Engine transforms canonical
trading records into independently verifiable
institutional evidence.
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
    SPACE_SM,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_verification_engine():

    """
    Builds the Verification Engine page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE VERIFICATION ENGINE",
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
            "Institutional trust is established "
            "through institutional verification.",
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
            "The Verification Engine is responsible "
            "for independently evaluating canonical "
            "trading records and determining whether "
            "they satisfy institutional verification "
            "requirements.",
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
            "Verification Infrastructure exists "
            "to transform trading activity into "
            "institutional evidence capable of "
            "supporting allocator-ready decision "
            "making.",
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
            "The Verification Engine is "
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

        "Institutional trade verification.",

        "Claim verification procedures.",

        "Evidence scoring.",

        "Integrity scoring.",

        "Governance scoring.",

        "Verification certificate generation.",

        "Institutional trust assessment.",

        "Verification lifecycle management.",

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
                SPACE_SM,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Verification is not the process of "
            "determining whether performance is "
            "good or bad.",
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
            "Verification is the process of "
            "determining whether performance can "
            "be independently trusted.",
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
            "Trading Truth Layer does not verify "
            "profitability. It verifies institutional "
            "trust in the underlying evidence.",
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

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Institutional verification transforms "
            "trading records into independently "
            "verifiable institutional evidence.",
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
            "Trust should never be assumed. "
            "It should be independently verified.",
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