"""
Trading Truth Layer

Volume IV

Trading Truth Layer Institutional Domains

Introduction
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


def build_introduction():

    """
    Builds the institutional introduction
    for Volume IV.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INTRODUCTION",
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
    # INSTITUTIONAL TRUST ECOSYSTEM
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional trust is not a single "
            "institutional capability.",
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
            "Modern capital markets require "
            "multiple institutional capabilities "
            "working together to establish "
            "independently verifiable trust.",
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
    # INSTITUTIONAL DOMAIN ARCHITECTURE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer operates as an "
            "institutional trust ecosystem "
            "composed of governed institutional "
            "domains.",
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
            "Each domain is responsible for a "
            "specific institutional function "
            "within the institutional trust "
            "lifecycle.",
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
    # INSTITUTIONAL DOMAIN RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL DOMAIN RESPONSIBILITIES",
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

        "Institutional evidence acquisition.",

        "Institutional evidence governance.",

        "Institutional claim operations.",

        "Institutional trust intelligence generation.",

        "Institutional investigations and due diligence.",

        "Institutional trust distribution.",

        "Institutional administration and governance.",

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
    # INSTITUTIONAL POSITIONING
    # --------------------------------------------------

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Institutional trust emerges only "
            "when all institutional domains "
            "operate together as a governed "
            "ecosystem.",
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
            "Volume IV introduces the institutional "
            "domains responsible for transforming "
            "trading activity into institutional "
            "trust across Trading Truth Layer.",
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