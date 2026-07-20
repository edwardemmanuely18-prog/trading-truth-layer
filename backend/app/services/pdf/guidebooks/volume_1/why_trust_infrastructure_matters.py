"""
Trading Truth Layer

Why Trust Infrastructure Matters

This page explains why institutional trust
infrastructure matters within global capital
markets and why evidence-based trust is
required for institutional capital allocation.
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


def build_why_trust_infrastructure_matters():
    """
    Builds the Why Trust Infrastructure Matters page.

    Returns
    -------
    list

        ReportLab flowables representing
        the complete page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHY TRUST INFRASTRUCTURE MATTERS",
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
            "Every year, billions of dollars are "
            "allocated based upon trading performance "
            "records across global capital markets.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    story.append(
        Paragraph(
            "Institutional capital allocation "
            "depends upon trust.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    story.append(
        Paragraph(
            "Trust depends upon evidence.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    story.append(
        Paragraph(
            "Evidence depends upon institutional "
            "infrastructure.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_LG)
    )

    story.append(
        Paragraph(
            "Yet there remains no institutional "
            "trust infrastructure layer capable "
            "of independently establishing trust "
            "in trading performance records.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    story.append(
        Paragraph(
            "Trading Truth Layer exists because "
            "institutional trust should not be optional.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    story.append(
        Paragraph(
            "Institutional trust should be "
            "infrastructure.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    story.append(
        Paragraph(
            "Evidence-based capital allocation "
            "begins with institutional trust.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        PageBreak()
    )

    return story


# ==========================================================
# END OF FILE
# ==========================================================