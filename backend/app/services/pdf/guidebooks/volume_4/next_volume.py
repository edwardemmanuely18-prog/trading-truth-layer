"""
Trading Truth Layer

Volume IV

Next Volume Preview

This module renders the institutional
preview of Volume V of the Trading Truth
Layer Guidebook Series.
"""

from reportlab.platypus import (
    Paragraph,
    Spacer,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    BODY_CENTER_STYLE,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# VOLUME V CONSTANTS
# ==========================================================

VOLUME_5_TITLE = (
    "Evidence-Based Capital Allocation"
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_next_volume():

    """
    Builds the institutional preview
    page for Volume V.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "NEXT VOLUME PREVIEW",
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
    # VOLUME V
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VOLUME V",
            TITLE_STYLE,
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
            VOLUME_5_TITLE,
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
    # INSTITUTIONAL QUESTION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL QUESTION",
            TITLE_STYLE,
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
            "How should institutions allocate capital "
            "using independently verifiable trading "
            "evidence?",
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
    # WHAT VOLUME V WILL ESTABLISH
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHAT VOLUME V WILL ESTABLISH",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    topics = [

        "Evidence-Based Capital Allocation.",

        "Institutional Due Diligence Standards.",

        "Allocator Decision Frameworks.",

        "Institutional Capital Allocation Intelligence.",

        "Trust-Based Investment Processes.",

        "Allocator-Ready Institutional Outputs.",

    ]

    for topic in topics:

        story.append(
            Paragraph(
                topic,
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
    # FUTURE INSTITUTIONAL CAPABILITIES
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "FUTURE INSTITUTIONAL CAPABILITIES",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    capabilities = [

        "Allocator-ready trust intelligence.",

        "Institutional capital allocation workflows.",

        "Evidence-based investment decisions.",

        "Institutional trust scoring models.",

        "Global allocator infrastructure.",

        "Independent institutional due diligence.",

    ]

    for capability in capabilities:

        story.append(
            Paragraph(
                capability,
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
    # GUIDEBOOK SERIES POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Volume V concludes the institutional "
            "capital allocation framework established "
            "throughout the Trading Truth Layer "
            "Guidebook Series.",
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
            "Institutional capital allocation should "
            "be governed by independently verifiable "
            "evidence rather than historical "
            "performance claims.",
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