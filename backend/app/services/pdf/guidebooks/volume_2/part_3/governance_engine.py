"""
Trading Truth Layer

Governance Engine

This module formally introduces the
Governance Engine and its institutional
responsibilities within Trading Truth
Layer's Verification Infrastructure.

The Governance Engine exists to govern
institutional trading evidence throughout
its verification lifecycle.
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


def build_governance_engine():

    """
    Builds the Governance Engine page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE GOVERNANCE ENGINE",
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
            "Institutional trust must be governed.",
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
            "The Governance Engine is responsible "
            "for managing the institutional "
            "verification lifecycle of trading "
            "evidence throughout Trading Truth Layer.",
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
            "Verification establishes institutional "
            "trust. Governance preserves institutional "
            "confidence in that trust over time.",
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
            "The Governance Engine is responsible for:",
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

        "Institutional claim lifecycle governance.",

        "Verification state management.",

        "Claim publication governance.",

        "Institutional approval workflows.",

        "Record locking procedures.",

        "Historical auditability.",

        "Verification governance policies.",

        "Institutional evidence stewardship.",

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
    # GOVERNANCE LIFECYCLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional evidence progresses "
            "through governed lifecycle states.",
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
            "Draft → Verify → Publish → Lock",
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
            "Every lifecycle transition is "
            "institutionally governed and "
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
    # INSTITUTIONAL POSITIONING
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Institutional trust is not merely "
            "verified. It is institutionally governed.",
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
            "Governance transforms verification "
            "into a repeatable institutional process "
            "capable of supporting global capital "
            "markets.",
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