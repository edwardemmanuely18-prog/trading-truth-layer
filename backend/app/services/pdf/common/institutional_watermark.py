from __future__ import annotations

from math import atan2, degrees

from reportlab.lib.colors import Color

from .institutional_theme import (

    PAGE_MARGIN,

    FOOTER_HEIGHT,

    TTL_WATERMARK,

    TTL_GREY,

    WATERMARK_OPACITY,

    WATERMARK_FONT_SIZE,

    DRAFT_WATERMARK_FONT_SIZE,

    CONFIDENTIAL_WATERMARK_FONT_SIZE,

    DOCUMENT_STATE_FONT_SIZE,

    VERIFIED_STAMP_FONT_SIZE,

    HASH_FONT_SIZE,

)


# ==========================================================
# WATERMARK STATES
# ==========================================================

WATERMARK_VERIFIED = "VERIFIED"

WATERMARK_DRAFT = "DRAFT"

WATERMARK_CONFIDENTIAL = "CONFIDENTIAL"

WATERMARK_INTERNAL = "INTERNAL"

WATERMARK_ARCHIVED = "ARCHIVED"

WATERMARK_CANCELLED = "CANCELLED"

WATERMARK_PUBLIC = "PUBLIC"


# ==========================================================
# INTERNAL WATERMARK ENGINE
# ==========================================================

def _draw_center_watermark(
    canvas,
    *,
    text: str,
    colour: Color,
    font_size: int,
    rotation: float = 30,
):
    """
    Canonical centered watermark renderer.

    Every document state should render through
    this function.
    """

    canvas.saveState()

    canvas.setFillColor(colour)

    canvas.setFont(
        "Helvetica-Bold",
        font_size,
    )

    width, height = canvas._pagesize

    canvas.translate(
        width / 2,
        height / 2,
    )

    canvas.rotate(rotation)

    canvas.drawCentredString(
        0,
        -20,
        text,
    )

    canvas.restoreState()

# ==========================================================
# CENTRAL WATERMARK
# ==========================================================

def draw_watermark(
    canvas,
    text: str = "TRADING TRUTH LAYER",
):

    colour = Color(
        TTL_WATERMARK.red,
        TTL_WATERMARK.green,
        TTL_WATERMARK.blue,
        alpha=WATERMARK_OPACITY,
    )

    _draw_center_watermark(
        canvas,
        text=text,
        colour=colour,
        font_size=WATERMARK_FONT_SIZE,
        rotation=30,
    )


# ==========================================================
# VERIFIED
# ==========================================================

def draw_verified_stamp(
    canvas,
):

    page_width, page_height = canvas._pagesize

    canvas.saveState()

    canvas.setFont(
        "Helvetica-Bold",
        VERIFIED_STAMP_FONT_SIZE,
    )

    canvas.setFillColorRGB(
        0.1,
        0.55,
        0.1,
    )

    canvas.drawRightString(

        page_width - PAGE_MARGIN,

        FOOTER_HEIGHT - 22,

        "TTL VERIFIED",

    )

    canvas.restoreState()


# ==========================================================
# DRAFT
# ==========================================================

def draw_draft_stamp(
    canvas,
):

    colour = Color(
        0.80,
        0.20,
        0.20,
        alpha=WATERMARK_OPACITY,
    )

    _draw_center_watermark(
        canvas,
        text="DRAFT",
        colour=colour,
        font_size=DRAFT_WATERMARK_FONT_SIZE,
        rotation=35,
    )


# ==========================================================
# CONFIDENTIAL
# ==========================================================

def draw_confidential_stamp(
    canvas,
):

    colour = Color(
        0.75,
        0.15,
        0.15,
        alpha=WATERMARK_OPACITY,
    )

    _draw_center_watermark(
        canvas,
        text="CONFIDENTIAL",
        colour=colour,
        font_size=CONFIDENTIAL_WATERMARK_FONT_SIZE,
        rotation=40,
    )

# ==========================================================
# DOCUMENT STATE
# ==========================================================

def draw_document_state(
    canvas,
    state: str,
):
    """
    Canonical document state renderer.

    Future reports should call this function
    instead of state-specific functions.
    """

    state = (state or "").strip().upper()

    if state == WATERMARK_VERIFIED:
        draw_verified_stamp(canvas)
        return

    if state == WATERMARK_DRAFT:
        draw_draft_stamp(canvas)
        return

    if state == WATERMARK_CONFIDENTIAL:
        draw_confidential_stamp(canvas)
        return

    if state == WATERMARK_INTERNAL:

        colour = Color(
            0.20,
            0.20,
            0.60,
            alpha=WATERMARK_OPACITY,
        )

        _draw_center_watermark(
            canvas,
            text="INTERNAL",
            colour=colour,
            font_size=DOCUMENT_STATE_FONT_SIZE,
            rotation=35,
        )
        return

    if state == WATERMARK_ARCHIVED:

        colour = Color(
            0.40,
            0.40,
            0.40,
            alpha=WATERMARK_OPACITY,
        )

        _draw_center_watermark(
            canvas,
            text="ARCHIVED",
            colour=colour,
            font_size=DOCUMENT_STATE_FONT_SIZE,
            rotation=35,
        )
        return

    if state == WATERMARK_CANCELLED:

        colour = Color(
            0.70,
            0.10,
            0.10,
            alpha=WATERMARK_OPACITY,
        )

        _draw_center_watermark(
            canvas,
            text="CANCELLED",
            colour=colour,
            font_size=DOCUMENT_STATE_FONT_SIZE,
            rotation=35,
        )
        return


# ==========================================================
# HASH
# ==========================================================

def draw_hash_watermark(
    canvas,
    report_hash: str,
):

    if not report_hash:
        return

    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        HASH_FONT_SIZE,
    )

    canvas.setFillColor(TTL_GREY)

    canvas.drawCentredString(

        canvas._pagesize[0]/2,

        16,

        f"Verification Hash: {report_hash}",

    )

    canvas.restoreState()

# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

#
# These wrappers intentionally remain to avoid
# breaking existing report modules while the
# framework migration is in progress.
#

def draw_verified_watermark(canvas):
    """
    Backward-compatible wrapper.
    """
    draw_verified_stamp(canvas)


def draw_draft_watermark(canvas):
    """
    Backward-compatible wrapper.
    """
    draw_draft_stamp(canvas)


def draw_confidential_watermark(canvas):
    """
    Backward-compatible wrapper.
    """
    draw_confidential_stamp(canvas)


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    #
    # Generic
    #

    "draw_watermark",

    "draw_document_state",

    #
    # States
    #

    "draw_verified_stamp",

    "draw_draft_stamp",

    "draw_confidential_stamp",

    #
    # Compatibility
    #

    "draw_verified_watermark",

    "draw_draft_watermark",

    "draw_confidential_watermark",

    #
    # Hash
    #

    "draw_hash_watermark",

    #
    # Constants
    #

    "WATERMARK_VERIFIED",

    "WATERMARK_DRAFT",

    "WATERMARK_CONFIDENTIAL",

    "WATERMARK_INTERNAL",

    "WATERMARK_ARCHIVED",

    "WATERMARK_CANCELLED",

    "WATERMARK_PUBLIC",

]