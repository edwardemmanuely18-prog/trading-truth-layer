from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from reportlab.lib.units import inch

from reportlab.platypus import (
    Paragraph,
    Spacer,
    KeepTogether,
)

from .institutional_theme import (
    BODY_STYLE,
    SPACE_MD,
)

from .institutional_sections import (
    build_section_title,
)


# ==========================================================
# SPACING
# ==========================================================

def gap(
    height=SPACE_MD,
):
    """
    Canonical institutional spacer.

    Height is expected to be in points/inches
    consistent with institutional_theme.
    """

    return Spacer(
        1,
        height,
    )


# ==========================================================
# FORMAT MONEY
# ==========================================================

def money(value):

    if value is None:

        return "-"

    return f"${float(value):,.2f}"


# ==========================================================
# FORMAT NUMBER
# ==========================================================

def number(value):

    if value is None:

        return "-"

    return f"{float(value):,.2f}"


# ==========================================================
# FORMAT PERCENT
# ==========================================================

def percent(value):

    if value is None:

        return "-"

    return f"{float(value):,.2f}%"


# ==========================================================
# FORMAT DATETIME
# ==========================================================

def timestamp(value):

    if not value:

        return "-"

    if isinstance(

        value,

        datetime,

    ):

        return value.strftime(

            "%Y-%m-%d %H:%M UTC"

        )

    return str(value)


# ==========================================================
# HASH SHORTENER
# ==========================================================

def short_hash(

    value,

    length=18,

):

    if not value:

        return "-"

    value=str(value)

    if len(value)<=length:

        return value

    return value[:length]+"..."


# ==========================================================
# STANDARD PARAGRAPH
# ==========================================================

def paragraph(text):

    return Paragraph(

        str(text),

        BODY_STYLE,

    )


# ==========================================================
# SECTION SPACER
# ==========================================================

def section_gap():
    """
    Backward-compatible section spacer.
    """

    return gap()


# ==========================================================
# SAFE VALUE
# ==========================================================

def safe(

    value,

    default="-",

):

    if value in {

        None,

        "",

    }:

        return default

    return value


# ==========================================================
# YES / NO
# ==========================================================

def yes_no(value):

    return "Yes" if value else "No"


# ==========================================================
# GRADE LABEL
# ==========================================================

def grade(score):
    if score is None:
        return "-"

    score = float(score)

    if score>=95:

        return "AAA"

    if score>=90:

        return "AA"

    if score>=85:

        return "A"

    if score>=75:

        return "BBB"

    if score>=65:

        return "BB"

    if score>=50:

        return "B"

    return "C"


# ==========================================================
# SECTION BLOCK
# ==========================================================

def build_section_block(
    title,
    content,
):
    """
    Backward-compatible wrapper.

    New code should prefer
    institutional_sections.build_section().
    """

    block = []

    block.extend(
        build_section_title(title)
    )

    if isinstance(content, (list, tuple)):
        block.extend(content)
    else:
        block.append(content)

    return KeepTogether(block)

# ==========================================================
# COMPATIBILITY ALIASES
# ==========================================================

format_money = money

format_number = number

format_percent = percent

format_timestamp = timestamp

# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "gap",
    "section_gap",

    "money",
    "number",
    "percent",
    "timestamp",

    "format_money",
    "format_number",
    "format_percent",
    "format_timestamp",

    "safe",
    "yes_no",
    "grade",

    "paragraph",

    "short_hash",

    "build_section_block",

]