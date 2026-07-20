"""
Trading Truth Layer

Verification Certificates

This module formally introduces
Verification Certificates as institutional
verification artifacts produced by Trading
Truth Layer's Verification Infrastructure.

Verification Certificates represent the
institutional conclusion of the verification
process.
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


def build_verification_certificates():

    """
    Builds the Verification Certificates page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION CERTIFICATES",
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
            "Institutional verification must "
            "produce institutionally meaningful "
            "outputs.",
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
            "Verification Certificates are the "
            "institutional artifacts produced "
            "upon completion of the verification "
            "workflow.",
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
            "They communicate the institutional "
            "conclusions reached by Trading Truth "
            "Layer's Verification Infrastructure.",
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
    # CERTIFICATE COMPONENTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Verification Certificates may include:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    components = [

        "Verification metrics.",

        "Evidence assessment results.",

        "Integrity assessment results.",

        "Governance assessment results.",

        "Institutional trust metrics.",

        "Verification bands and classifications.",

        "Institutional verification conclusions.",

        "Historical verification records.",

    ]

    for component in components:

        story.append(
            Paragraph(
                f"• {component}",
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
    # INSTITUTIONAL VALUE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Verification Certificates provide "
            "institutions with independently "
            "generated verification intelligence.",
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
            "They are designed to support "
            "institutional review, allocator "
            "decision-making and evidence-based "
            "trust assessments.",
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
            "Institutional trust should be "
            "communicated through institutional "
            "artifacts rather than assumptions.",
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
            "Verification Certificates represent "
            "the institutional conclusions of "
            "Trading Truth Layer's Verification "
            "Infrastructure.",
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