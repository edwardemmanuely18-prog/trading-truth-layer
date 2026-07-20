"""
Trading Truth Layer

Conclusion

This module renders the institutional
closing statement for Volume II of the
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
    page for Volume II.
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
            "Institutional trust cannot exist "
            "without institutional verification.",
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
            "Modern capital markets require "
            "verification infrastructure capable "
            "of independently establishing trust "
            "in trading evidence.",
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
    # WHAT VOLUME II ESTABLISHED
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Volume II establishes how "
            "Institutional Verification "
            "Infrastructure transforms trading "
            "activity into independently "
            "verifiable institutional evidence.",
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
            "Verification Infrastructure is "
            "responsible for establishing "
            "institutional confidence in "
            "trading performance records.",
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
    # THE GUIDEBOOK SERIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The Trading Truth Layer Guidebook "
            "Series establishes the institutional "
            "pipeline of evidence-based capital "
            "allocation.",
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

        "Volume I - Why Institutional Trading Trust Infrastructure must exist.",

        "Volume II - How Institutional Verification Infrastructure independently establishes trust.",

        "Volume III - How institutions perform due diligence on independently verified evidence.",

        "Volume IV - How institutions allocate capital using evidence-based trust.",

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
    # INSTITUTIONAL CLOSING STATEMENT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Verification Infrastructure is not "
            "an optional capability of modern "
            "capital markets. It is an inevitable "
            "institutional requirement.",
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
            "Independent verification will become "
            "the institutional standard for "
            "evidence-based capital allocation.",
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
            "Trading Truth Layer exists to establish "
            "the Verification Infrastructure required "
            "to independently create institutional "
            "trust across global capital markets.",
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