from __future__ import annotations

"""
Trading Truth Layer
Institutional Badge Framework

Provides canonical badge rendering used across every
institutional report.

No report should construct coloured status badges
directly.

Examples

Verified
Failed
Conditional
AAA
AA
A
BBB
Critical
High
Medium
Low
"""

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from .institutional_theme import (
    TTL_GREEN,
    TTL_RED,
    TTL_AMBER,
    TTL_BLUE,
    TTL_NAVY,
)


# ==========================================================
# COLOUR ENGINE
# ==========================================================


def badge_colour(value: str):

    value = str(value).strip().upper()

    if value in {

        "VERIFIED",
        "PASSED",
        "APPROVED",
        "VALID",
        "AAA",
        "AA",

    }:

        return TTL_GREEN

    if value in {

        "A",
        "CONDITIONAL",
        "CONDITIONAL_ACCEPT",
        "REVIEW",

    }:

        return TTL_AMBER

    if value in {

        "FAILED",
        "REJECTED",
        "CRITICAL",
        "HIGH",

    }:

        return TTL_RED

    return TTL_BLUE


# ==========================================================
# STYLE
# ==========================================================


def _badge_style(colour):

    return ParagraphStyle(

        "InstitutionalBadge",

        alignment=TA_CENTER,

        textColor="white",

        backColor=colour,

        fontName="Helvetica-Bold",

        fontSize=8,

        leading=10,

        borderPadding=(4, 8, 4),

    )


# ==========================================================
# BUILDER
# ==========================================================


def build_badge(

    value: str,

):

    colour = badge_colour(value)

    return Paragraph(

        f"<b>{value}</b>",

        _badge_style(colour),

    )


__all__ = [

    "build_badge",

    "badge_colour",

]