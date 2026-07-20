"""
Trading Truth Layer

Guidebook Cover Rendering Framework

Canonical cover page renderer for all
Trading Truth Layer institutional guidebooks.

This module intentionally consumes the existing
institutional PDF design system and introduces
NO guidebook-specific typography or styling.

All guidebook cover pages must be rendered
through this module.
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
    SPACE_SM,
    SPACE_MD,
    SPACE_XL,
    COVER_TOP_SPACING,
    COVER_SECTION_SPACING,
)

from app.services.pdf.guidebooks.common.guidebook_constants import (
    GUIDEBOOK_SERIES_NAME,
    GUIDEBOOK_SERIES_VERSION,
    GUIDEBOOK_WEBSITE,
    GUIDEBOOK_YEAR,
)


# ==========================================================
# INTERNAL HELPERS
# ==========================================================


def _build_volume_title(
    volume_number: int,
) -> Paragraph:
    """
    Builds the canonical volume title.

    Example:

    VOLUME I
    VOLUME II
    VOLUME III
    """

    return Paragraph(
        f"VOLUME {volume_number}",
        TITLE_STYLE,
    )


def _build_publication_type(
    publication_type: str,
) -> Paragraph:
    """
    Builds the guidebook publication type.
    """

    return Paragraph(
        publication_type,
        SUBTITLE_STYLE,
    )


# ==========================================================
# PUBLIC API
# ==========================================================


def build_guidebook_cover(
    volume_number: int,
    title: str,
    subtitle: str,
    publication_type: str,
):
    """
    Builds the canonical Trading Truth Layer
    Guidebook Series cover page.

    Parameters
    ----------
    volume_number:
        Guidebook volume number.

    title:
        Official volume title.

    subtitle:
        Institutional positioning statement.

    publication_type:
        Institutional Whitepaper /
        Institutional Guidebook /
        Institutional Publication.

    Returns
    -------
    list

        ReportLab Flowables representing
        the complete guidebook cover page.
    """

    story = []

    # ------------------------------------------------------
    # TOP SPACING
    # ------------------------------------------------------

    story.append(
        Spacer(1, COVER_TOP_SPACING)
    )

    # ------------------------------------------------------
    # GUIDEBOOK SERIES NAME
    # ------------------------------------------------------

    story.append(
        Paragraph(
            GUIDEBOOK_SERIES_NAME,
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_SM)
    )

    # ------------------------------------------------------
    # VOLUME NUMBER
    # ------------------------------------------------------

    story.append(
        _build_volume_title(
            volume_number
        )
    )

    story.append(
        Spacer(
            1,
            COVER_SECTION_SPACING,
        )
    )

    # ------------------------------------------------------
    # GUIDEBOOK TITLE
    # ------------------------------------------------------

    story.append(
        Paragraph(
            title,
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_XL,
        )
    )

    # ------------------------------------------------------
    # PUBLICATION TYPE
    # ------------------------------------------------------

    story.append(
        _build_publication_type(
            publication_type
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # ------------------------------------------------------
    # SUBTITLE
    # ------------------------------------------------------

    story.append(
        Paragraph(
            subtitle,
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_XL,
        )
    )

    # ------------------------------------------------------
    # VERSION
    # ------------------------------------------------------

    story.append(
        Paragraph(
            f"Guidebook Series v{GUIDEBOOK_SERIES_VERSION}",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_SM,
        )
    )

    # ------------------------------------------------------
    # WEBSITE
    # ------------------------------------------------------

    story.append(
        Paragraph(
            GUIDEBOOK_WEBSITE,
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_SM,
        )
    )

    # ------------------------------------------------------
    # YEAR
    # ------------------------------------------------------

    story.append(
        Paragraph(
            GUIDEBOOK_YEAR,
            BODY_CENTER_STYLE,
        )
    )

    # ------------------------------------------------------
    # COVER PAGE BREAK
    # ------------------------------------------------------

    story.append(
        PageBreak()
    )

    return story