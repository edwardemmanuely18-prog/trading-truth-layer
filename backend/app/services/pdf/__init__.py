from __future__ import annotations

from datetime import datetime

from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer

from app.services.pdf.common.institutional_theme import (
    BODY_STYLE,
)


# ==========================================================
# MONEY
# ==========================================================

def money(value):

    if value is None:
        return "-"

    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "-"


# ==========================================================
# NUMBER
# ==========================================================

def number(value):

    if value is None:
        return "-"

    try:
        return f"{float(value):,.2f}"
    except Exception:
        return "-"


# ==========================================================
# PERCENT
# ==========================================================

def percent(value):

    if value is None:
        return "-"

    try:
        return f"{float(value):,.2f}%"
    except Exception:
        return "-"


# ==========================================================
# DATETIME
# ==========================================================

def timestamp(value):

    if not value:
        return "-"

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M UTC")

    return str(value)


# ==========================================================
# HASH
# ==========================================================

def short_hash(
    value,
    length: int = 18,
):

    if not value:
        return "-"

    value = str(value)

    if len(value) <= length:
        return value

    return value[:length] + "..."


# ==========================================================
# PARAGRAPH
# ==========================================================

def paragraph(text):

    return Paragraph(
        str(text),
        BODY_STYLE,
    )


# ==========================================================
# SPACING
# ==========================================================

def section_gap():

    return Spacer(
        1,
        0.20 * inch,
    )


# ==========================================================
# SAFE
# ==========================================================

def safe(
    value,
    default="-",
):

    if value in (
        None,
        "",
    ):
        return default

    return value


# ==========================================================
# BOOLEAN
# ==========================================================

def yes_no(value):

    return "Yes" if bool(value) else "No"


# ==========================================================
# GRADE
# ==========================================================

def grade(score):

    try:
        score = float(score)
    except Exception:
        return "-"

    if score >= 95:
        return "AAA"

    if score >= 90:
        return "AA"

    if score >= 85:
        return "A"

    if score >= 75:
        return "BBB"

    if score >= 65:
        return "BB"

    if score >= 50:
        return "B"

    return "C"


__all__ = [
    "BODY_STYLE",
    "money",
    "number",
    "percent",
    "timestamp",
    "short_hash",
    "paragraph",
    "section_gap",
    "safe",
    "yes_no",
    "grade",
]