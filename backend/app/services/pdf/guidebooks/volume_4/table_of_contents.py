"""
Trading Truth Layer

Volume IV

Table of Contents

This module renders the institutional
Table of Contents for Volume IV of the
Trading Truth Layer Guidebook Series.
"""

from reportlab.platypus import (
    Paragraph,
    Spacer,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    SUBTITLE_STYLE,
    BODY_CENTER_STYLE,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_table_of_contents():

    """
    Builds the institutional Table of
    Contents page for Volume IV.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TABLE OF CONTENTS",
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
    # PART I
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PART I",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "THE INSTITUTIONAL CAPITAL "
            "ALLOCATION PROBLEM",
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
    # PART II
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PART II",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "DOMAIN DOCUMENTATION "
            "METHODOLOGY",
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
    # PART III
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PART III",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "TTL INSTITUTIONAL DOMAINS",
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
    # DOMAIN I
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN I",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "EXECUTIVE WORKSPACE "
            "INFRASTRUCTURE",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Paragraph(
            "(DASHBOARD)",
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
    # DOMAIN II
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN II",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "INSTITUTIONAL EVIDENCE "
            "INFRASTRUCTURE",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Paragraph(
            "(EVIDENCE INTAKE)",
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
    # DOMAIN III
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN III",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "CANONICAL EVIDENCE "
            "INFRASTRUCTURE",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Paragraph(
            "(EVIDENCE REGISTRY)",
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
    # DOMAIN IV
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "DOMAIN IV",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "CLAIM INFRASTRUCTURE",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Paragraph(
            "(CLAIM OPERATIONS)",
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
    # DOMAIN V
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN V",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "TRUST INTELLIGENCE "
            "INFRASTRUCTURE",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Paragraph(
            "(TRUST INTELLIGENCE)",
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
    # DOMAIN VI
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN VI",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "INSTITUTIONAL INVESTIGATION "
            "INFRASTRUCTURE",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Paragraph(
            "(INVESTIGATION CENTER)",
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
    # DOMAIN VII
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN VII",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "PUBLIC TRUST "
            "INFRASTRUCTURE",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Paragraph(
            "(PUBLIC TRUST LAYER)",
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
    # DOMAIN VIII
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN VIII",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "WORKSPACE GOVERNANCE "
            "INFRASTRUCTURE",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Paragraph(
            "(ADMINISTRATION)",
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
            "CONCLUSION",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # NEXT VOLUME PREVIEW
    # --------------------------------------------------

    story.append(
        Paragraph(
            "NEXT VOLUME PREVIEW",
            SUBTITLE_STYLE,
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