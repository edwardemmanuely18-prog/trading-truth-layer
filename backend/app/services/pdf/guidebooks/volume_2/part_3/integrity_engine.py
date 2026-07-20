"""
Trading Truth Layer

Integrity Engine

This module formally introduces the
Integrity Engine and its institutional
responsibilities within Trading Truth
Layer's Verification Infrastructure.

The Integrity Engine exists to preserve
the integrity of institutional trading
evidence throughout the verification
lifecycle.
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


def build_integrity_engine():

    """
    Builds the Integrity Engine page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE INTEGRITY ENGINE",
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
            "Institutional verification is only "
            "valuable if the integrity of the "
            "underlying evidence is preserved.",
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
            "The Integrity Engine is responsible "
            "for ensuring that institutional "
            "trading evidence remains complete, "
            "consistent and trustworthy throughout "
            "the verification lifecycle.",
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
            "Institutional trust cannot exist "
            "without institutional integrity.",
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
            "The Integrity Engine is responsible for:",
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

        "Evidence integrity analysis.",

        "Claim integrity monitoring.",

        "Historical record preservation.",

        "Integrity score generation.",

        "Verification consistency checks.",

        "Evidence lineage preservation.",

        "Institutional auditability.",

        "Tamper-evident integrity procedures.",

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
            "Verification establishes trust in "
            "trading evidence.",
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
            "Integrity preserves that trust "
            "throughout the institutional "
            "verification lifecycle.",
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
            "Institutional evidence should be "
            "tamper-evident, audit-ready and "
            "historically preserved.",
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
            "Trust without integrity is merely "
            "an assumption. Institutional trust "
            "requires institutional integrity.",
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