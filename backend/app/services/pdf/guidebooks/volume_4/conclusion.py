"""
Trading Truth Layer

Volume IV

Conclusion

This module renders the institutional
closing statement for Volume IV of the
Trading Truth Layer Guidebook Series.
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


def build_conclusion():

    """
    Builds the institutional conclusion
    page for Volume IV.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CONCLUSION",
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
            "Institutional capital allocation requires "
            "institutional trust infrastructure.",
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
            "Trading Truth Layer establishes the institutional "
            "infrastructure required to transform trading "
            "activity into allocator-ready trust records.",
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
    # WHAT VOLUME IV ESTABLISHED
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Volume IV establishes the institutional "
            "operating infrastructure of Trading Truth Layer.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    established_components = [

        "Executive Workspace Infrastructure.",

        "Institutional Evidence Infrastructure.",

        "Canonical Evidence Infrastructure.",

        "Claim Infrastructure.",

        "Trust Intelligence Infrastructure.",

        "Institutional Investigation Infrastructure.",

        "Public Trust Infrastructure.",

        "Workspace Governance Infrastructure.",

    ]

    for component in established_components:

        story.append(
            Paragraph(
                f"• {component}",
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
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # THE INSTITUTIONAL TRUST LIFECYCLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The institutional trust lifecycle documented "
            "throughout the Guidebook Series now consists of:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    trust_lifecycle = [

        "Institutional Trust Infrastructure.",

        "Verification Infrastructure.",

        "Trading Verification Infrastructure.",

        "Institutional Capital Allocation Infrastructure.",

    ]

    for item in trust_lifecycle:

        story.append(
            Paragraph(
                f"• {item}",
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
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # GUIDEBOOK SERIES PROGRESSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The Trading Truth Layer Guidebook Series "
            "documents the complete institutional trust "
            "pipeline for evidence-based capital allocation.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    guidebook_progression = [

        "Volume I - Why institutional trading trust infrastructure must exist.",

        "Volume II - How institutional verification infrastructure establishes trust.",

        "Volume III - How trading performance becomes institutionally verified.",

        "Volume IV - How institutional infrastructures collectively support allocator-ready trust records.",

        "Volume V - How institutions allocate capital using evidence-based trust.",

    ]

    for volume in guidebook_progression:

        story.append(
            Paragraph(
                f"• {volume}",
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
            "Trading Truth Layer is not a traditional "
            "trading analytics platform.",
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
            "It is an Institutional Trust Infrastructure "
            "designed to support evidence-based capital "
            "allocation across global capital markets.",
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
            "Institutional capital should be allocated "
            "upon independently verifiable evidence rather "
            "than historical performance claims.",
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
    # PAGE BREAK
    # --------------------------------------------------

    story.append(
        PageBreak()
    )

    return story


# ==========================================================
# END OF FILE
# ==========================================================