"""
Trading Truth Layer

Next Volume Preview Framework

Canonical next volume preview renderer for all
Trading Truth Layer Guidebooks.

This module creates institutional continuity
across the entire Guidebook Series by presenting
the next volume's institutional question and
major topics.

All guidebooks must consume this component.
"""

from reportlab.platypus import (

    Paragraph,
    Spacer,
    PageBreak,

)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    SUBTITLE_STYLE,
    BODY_STYLE,
    BODY_CENTER_STYLE,
    SPACE_SM,
    SPACE_MD,
    SPACE_LG,
)

from app.services.pdf.guidebooks.common.guidebook_constants import (
    GUIDEBOOK_SERIES_NAME,
    NEXT_VOLUME_METADATA,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_next_volume_preview(
    current_volume: int,
):
    """
    Builds the canonical next volume preview page.

    Parameters
    ----------
    current_volume:
        Current guidebook volume number.

    Returns
    -------
    list

        ReportLab flowables representing
        the next volume preview page.
    """

    if current_volume not in NEXT_VOLUME_METADATA:
        return []

    metadata = NEXT_VOLUME_METADATA[current_volume]

    next_volume = metadata["next_volume"]
    title = metadata["title"]
    institutional_question = metadata["institutional_question"]
    topics = metadata["topics"]

    story = []

    # --------------------------------------------------
    # SECTION TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE JOURNEY CONTINUES",
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
    # VOLUME NUMBER
    # --------------------------------------------------

    story.append(
        Paragraph(
            f"VOLUME {next_volume}",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # NEXT VOLUME TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            title,
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
    # INSTITUTIONAL QUESTION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional Question",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_SM,
        )
    )

    story.append(
        Paragraph(
            institutional_question,
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
    # TOPICS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The Next Volume Explores:",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_SM,
        )
    )

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
                SPACE_SM,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # GUIDEBOOK SERIES NAME
    # --------------------------------------------------

    story.append(
        Paragraph(
            GUIDEBOOK_SERIES_NAME,
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