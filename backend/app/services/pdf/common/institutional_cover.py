from __future__ import annotations

"""
Trading Truth Layer
Institutional Cover Framework

Provides the canonical cover page used by every
institutional report.

The cover builder is intentionally report-agnostic.

Supported reports

• Allocator Report

• Claim Report

• Verification Report

• Audit Report

• Evidence Pack

• Enterprise Reports
"""

from reportlab.platypus import (

    Paragraph,

    Spacer,

    Table,

    TableStyle,

)

from reportlab.lib import colors

from reportlab.lib.units import inch

from .institutional_theme import (

    TITLE_STYLE,

    SUBTITLE_STYLE,

    SCORE_STYLE,

    VERDICT_STYLE,

    BODY_STYLE,

    CAPTION_STYLE,

    TTL_NAVY,

    TTL_LIGHT,

    TTL_BORDER,

    SPACE_SM,

    SPACE_MD,

    SPACE_LG,

    QR_SIZE,

    CONTENT_WIDTH,

)

from .institutional_tables import (

    build_key_value_table,

    build_scorecard_table,

)

from .institutional_qr import (
    build_qr,
)

from reportlab.platypus import KeepTogether

# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _gap(height):

    return Spacer(

        1,

        height,

    )


def _paragraph(

    text,

    style,

):

    return Paragraph(

        str(text),

        style,

    )

# ==========================================================
# COVER HEADER
# ==========================================================

def _header_block(
    title,
    subtitle,
):
    """
    Institutional cover header.
    """

    return [

        _paragraph(
            "TRADING TRUTH LAYER",
            TITLE_STYLE,
        ),

        _gap(2),

        _paragraph(
            "Institutional Verification Infrastructure",
            CAPTION_STYLE,
        ),

        _gap(2),

        _paragraph(
            title,
            TITLE_STYLE,
        ),

        _gap(2),

        _paragraph(
            subtitle,
            SUBTITLE_STYLE,
        ),

    ]

# ==========================================================
# SCORE PANEL
# ==========================================================

def _score_panel(
    score,
    band,
):
    """
    Institutional executive score panel.
    """

    table = build_scorecard_table(

        title="Verification Score",

        score=score,

        band=band,

    )

    return [

        table,

    ]


# ==========================================================
# COVER METADATA
# ==========================================================

def _metadata_block(
    metadata,
):
    """
    Canonical metadata block.

    Delegates rendering to the
    institutional table framework.
    """

    display_metadata = dict(metadata)

    display_metadata.pop(
        "Verification URL",
        None,
    )

    table = build_key_value_table(
        display_metadata,
    )

    return [

        table,

        _gap(0),

    ]


# ==========================================================
# QR BLOCK
# ==========================================================

def _qr_block(
    metadata,
):

    url = metadata.get("Verification URL")

    if not url:
        return []

    qr = build_qr(url)

    qr_table = Table(
        [[qr]],
        colWidths=[CONTENT_WIDTH],
        hAlign="CENTER",
    )

    qr_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    caption = _paragraph(
        "Scan to verify this report",
        CAPTION_STYLE,
    )

    # Keep the caption attached to the QR table
    caption.keepWithPrevious = True

    return [
        qr_table,
        caption,
        _gap(2),
    ]


# ==========================================================
# COVER DISCLAIMER
# ==========================================================

def _classification_block(
    classification,
):
    """
    Institutional document
    classification notice.
    """

    return [

        _paragraph(
            classification,
            CAPTION_STYLE,
        ),

    ]

# ==========================================================
# COVER NOTICE
# ==========================================================

def _notice_block(
    notice,
):
    """
    Optional executive notice.
    """

    if not notice:

        return []

    return [

        _gap(2),

        _paragraph(
            notice,
            BODY_STYLE,
        ),

    ]


# ==========================================================
# PUBLIC BUILDER
# ==========================================================

def build_cover(
    *,
    title,
    subtitle,
    score,
    band,
    metadata,
    classification="Trading Truth Layer Confidential Institutional Document",

    notice: str | None = None,
):
    """
    Canonical institutional cover.

    Every report should consume
    this builder.
    """

    story = []

    #
    # Header
    #

    story.extend(

        _header_block(

            title,

            subtitle,

        )

    )

    story.append(
        _gap(2)
    )

    #
    # Score
    #

    story.extend(

        _score_panel(

            score,

            band,

        )

    )

    story.append(
        _gap(2)
    )

    story.extend(
        _metadata_block(metadata)
    )

    story.extend(
        _qr_block(metadata)
    )

    story.extend(
        _classification_block(classification)
    )

    story.extend(
        _notice_block(notice)
    )

    return story

# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def build_institutional_cover(*args, **kwargs):
    """
    Backward-compatible alias.

    Existing report modules still import
    build_institutional_cover().
    """

    return build_cover(*args, **kwargs)