from __future__ import annotations

"""
Trading Truth Layer
Institutional PDF Framework

Header / Footer Engine

Responsibilities
----------------

• Institutional page header
• Institutional page footer
• Document identity
• Report metadata
• Pagination

This module intentionally does NOT render:

• Watermarks
• VERIFIED stamps
• Draft stamps
• QR codes

Those belong to their dedicated modules.
"""

from reportlab.pdfgen.canvas import Canvas

from .institutional_theme import (
    PAGE_MARGIN,
    HEADER_HEIGHT,
    FOOTER_HEIGHT,
    PAGE_WIDTH,
    PAGE_HEIGHT,

    PRIMARY_TEXT,
    SECONDARY_TEXT,
    TTL_GREY,

    HEADER_BRAND_FONT_SIZE,
    HEADER_SUBTITLE_FONT_SIZE,
    HEADER_REPORT_FONT_SIZE,
    HEADER_VERSION_FONT_SIZE,

    FOOTER_FONT_SIZE,
    FOOTER_HASH_FONT_SIZE,
)


# ==========================================================
# INTERNAL TYPOGRAPHY
# ==========================================================

_HEADER_TITLE_FONT = "Helvetica-Bold"

_HEADER_TEXT_FONT = "Helvetica"

# ==========================================================
# HEADER LAYOUT
# ==========================================================

HEADER_TOP = PAGE_HEIGHT - PAGE_MARGIN

HEADER_BRAND_Y = HEADER_TOP - 6

HEADER_SUBTITLE_Y = HEADER_BRAND_Y - 14

HEADER_REPORT_Y = HEADER_TOP - 6

HEADER_REPORT_SUBTITLE_Y = HEADER_REPORT_Y - 14

HEADER_VERSION_Y = HEADER_REPORT_SUBTITLE_Y - 12

#
# Move divider UP so content begins below it.
#
HEADER_LINE_Y = HEADER_VERSION_Y - 6


# ==========================================================
# FOOTER LAYOUT
# ==========================================================

FOOTER_LINE_Y = FOOTER_HEIGHT + 30

FOOTER_TEXT_Y = FOOTER_HEIGHT + 4

FOOTER_CENTER_Y = FOOTER_HEIGHT + 8

FOOTER_PAGE_Y = FOOTER_HEIGHT + 8

HASH_Y = FOOTER_HEIGHT - 8

# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _draw_divider(
    canvas: Canvas,
    y: float,
):
    """
    Draw a full-width divider line.
    """

    canvas.setStrokeColor(TTL_GREY)

    canvas.line(
        PAGE_MARGIN,
        y,
        PAGE_WIDTH - PAGE_MARGIN,
        y,
    )


def _draw_brand(
    canvas: Canvas,
):
    """
    Draw Trading Truth Layer branding.
    """

    canvas.setFillColor(PRIMARY_TEXT)

    canvas.setFont(
        _HEADER_TITLE_FONT,
        HEADER_BRAND_FONT_SIZE,
    )

    canvas.drawString(
        PAGE_MARGIN,
        HEADER_BRAND_Y,
        "TRADING TRUTH LAYER",
    )

    canvas.setFont(
        _HEADER_TEXT_FONT,
        HEADER_SUBTITLE_FONT_SIZE,
    )

    canvas.setFillColor(
        SECONDARY_TEXT,
    )

    canvas.drawString(
        PAGE_MARGIN,
        HEADER_SUBTITLE_Y,
        "Institutional Verification Infrastructure",
    )


def _draw_report_identity(
    canvas: Canvas,
    *,
    title: str,
    subtitle: str | None,
    tvs_version: str,
):
    """
    Draw report identity on the
    upper-right corner.
    """

    right = PAGE_WIDTH - PAGE_MARGIN

    canvas.setFillColor(PRIMARY_TEXT)

    canvas.setFont(
        _HEADER_TITLE_FONT,
        HEADER_REPORT_FONT_SIZE,
    )

    canvas.drawRightString(
        right,
        HEADER_REPORT_Y,
        title,
    )

    if subtitle:

        canvas.setFont(
            _HEADER_TEXT_FONT,
            9,
        )

        canvas.setFillColor(
            SECONDARY_TEXT,
        )

        canvas.drawRightString(
            right,
            HEADER_REPORT_SUBTITLE_Y,
            subtitle,
        )

        version_y = HEADER_VERSION_Y

    else:

        version_y = HEADER_REPORT_SUBTITLE_Y

    canvas.setFont(
        _HEADER_TEXT_FONT,
        HEADER_VERSION_FONT_SIZE,
    )

    canvas.drawRightString(
        right,
        version_y,
        tvs_version,
    )


# ==========================================================
# PUBLIC HEADER
# ==========================================================

def draw_header(
    canvas: Canvas,
    title: str,
    subtitle: str | None = None,
    tvs_version: str = "",
):

    if canvas.getPageNumber() == 1:
        return

    """
    Draw institutional header.

    This function is report-agnostic and
    should be reused by every TTL report.
    """

    canvas.saveState()

    _draw_brand(canvas)

    _draw_report_identity(
        canvas,
        title=title,
        subtitle=subtitle,
        tvs_version=tvs_version,
    )

    _draw_divider(
        canvas,
        HEADER_LINE_Y,
    )

    canvas.restoreState()


# ==========================================================
# INTERNAL FOOTER HELPERS
# ==========================================================

def _draw_footer_identity(
    canvas: Canvas,
):
    """
    Draw footer identity.

    Left aligned.
    """

    canvas.setFont(
        _HEADER_TEXT_FONT,
        FOOTER_FONT_SIZE,
    )

    canvas.setFillColor(
        SECONDARY_TEXT,
    )

    canvas.drawString(
        PAGE_MARGIN,
        FOOTER_TEXT_Y,
        "Trading Truth Layer",
    )


def _draw_footer_metadata(
    canvas: Canvas,
    *,
    report_hash: str | None = None,
):
    """
    Draw footer metadata.

    Center aligned.
    """

    if not report_hash:
        return

    canvas.setFont(
        _HEADER_TEXT_FONT,
        FOOTER_HASH_FONT_SIZE,
    )

    canvas.setFillColor(
        SECONDARY_TEXT,
    )

    canvas.drawCentredString(
        PAGE_WIDTH / 2,
        HASH_Y,
        f"Verification Hash • {report_hash[:20]}..."
    )


def _draw_footer_page(
    canvas: Canvas,
    page_number: int,
):
    """
    Draw page number.

    Right aligned.
    """

    canvas.setFont(
        _HEADER_TEXT_FONT,
        FOOTER_FONT_SIZE,
    )

    canvas.setFillColor(
        SECONDARY_TEXT,
    )

    canvas.drawRightString(
        PAGE_WIDTH - PAGE_MARGIN,
        FOOTER_TEXT_Y,
        f"TTL VERIFIED   |   Page {page_number}",
    )


# ==========================================================
# PUBLIC FOOTER
# ==========================================================

def draw_footer(
    canvas: Canvas,
    doc,
    report_hash: str | None = None,
):

    if canvas.getPageNumber() == 1:
        return

    """
    Draw institutional footer.

    This implementation is report agnostic.

    Parameters
    ----------

    canvas

        ReportLab canvas.

    doc

        Current document.

    report_hash

        Optional report hash displayed
        in the footer.
    """

    canvas.saveState()

    _draw_divider(
        canvas,
        FOOTER_LINE_Y,
    )

    _draw_footer_identity(
        canvas,
    )

    _draw_footer_metadata(
        canvas,
        report_hash=report_hash,
    )

    _draw_footer_page(
        canvas,
        doc.page,
    )

    canvas.restoreState()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "draw_header",

    "draw_footer",

]