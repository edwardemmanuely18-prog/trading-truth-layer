from __future__ import annotations

"""
Trading Truth Layer
Institutional Table Framework

This module provides every canonical table used by
Trading Truth Layer institutional reports.

Responsibilities
----------------

• Default institutional tables
• Executive matrices
• Metric tables
• Score tables
• Timeline tables
• Comparison tables
• Summary tables

No report should construct a ReportLab TableStyle
directly. Every table should flow through this module.
"""

from reportlab.lib import colors
from reportlab.lib.units import inch

from reportlab.platypus import (
    Table,
    TableStyle,
)

from .institutional_theme import (

    #
    # Colours
    #

    TTL_NAVY,
    TTL_LIGHT,
    TTL_BORDER,
    TTL_GREEN,
    TTL_RED,
    TTL_GREY,

    #
    # Table Metrics
    #

    TABLE_CELL_PADDING,
    TABLE_HEADER_PADDING,
    TABLE_ROW_PADDING,
    TABLE_BORDER_WIDTH,
    TABLE_GRID_WIDTH,
    CONTENT_WIDTH,

    #
    # Typography
    #

    TABLE_FONT_NAME,
    TABLE_HEADER_FONT_NAME,
    TABLE_FONT_SIZE,
    TABLE_HEADER_FONT_SIZE,

)

# ==========================================================
# INTERNAL STYLE ENGINE
# ==========================================================

def _default_table_style():

    """
    Canonical institutional table style.

    Every table derives from this.
    """

    return TableStyle(

        [

            (
                "GRID",
                (0,0),
                (-1,-1),
                TABLE_GRID_WIDTH,
                TTL_BORDER,
            ),

            (
                "BOX",
                (0,0),
                (-1,-1),
                TABLE_BORDER_WIDTH,
                TTL_BORDER,
            ),

            (
                "BACKGROUND",
                (0,0),
                (-1,0),
                TTL_NAVY,
            ),

            (
                "TEXTCOLOR",
                (0,0),
                (-1,0),
                colors.white,
            ),

            (
                "FONTNAME",
                (0,0),
                (-1,0),
                TABLE_HEADER_FONT_NAME,
            ),

            (
                "FONTNAME",
                (0,1),
                (-1,-1),
                TABLE_FONT_NAME,
            ),

            (
                "FONTSIZE",
                (0,1),
                (-1,-1),
                TABLE_FONT_SIZE,
            ),

            (
                "FONTSIZE",
                (0,0),
                (-1,0),
                TABLE_HEADER_FONT_SIZE,
            ),

            (
                "TOPPADDING",
                (0,0),
                (-1,-1),
                TABLE_HEADER_PADDING,
            ),

            (
                "BOTTOMPADDING",
                (0,0),
                (-1,-1),
                TABLE_ROW_PADDING,
            ),

            (
                "LEFTPADDING",
                (0,0),
                (-1,-1),
                TABLE_CELL_PADDING,
            ),

            (
                "RIGHTPADDING",
                (0,0),
                (-1,-1),
                TABLE_CELL_PADDING,
            ),

            (
                "VALIGN",
                (0,0),
                (-1,-1),
                "MIDDLE",
            ),

            (
                "ROWBACKGROUNDS",
                (0,1),
                (-1,-1),
                [
                    colors.white,
                    TTL_LIGHT,
                ],
            ),

        ]

    )

# ==========================================================
# INTERNAL BUILDERS
# ==========================================================

def _build_table(
    rows,
    *,
    col_widths=None,
    repeat_rows: int = 1,
    h_align: str = "LEFT",
):

    #
    # Validate the incoming dataset
    #
    rows = validate_table_rows(rows)

    #
    # Normalize every table cell into a string.
    # This prevents unsupported objects from
    # reaching ReportLab.
    #
    normalized = []

    for row in rows:

        current = []

        for cell in row:

            if isinstance(cell, str):
                current.append(cell)
            else:
                current.append(str(cell))

        normalized.append(current)

    rows = normalized

    table = Table(
        rows,
        colWidths=col_widths,
        repeatRows=repeat_rows,
        hAlign="CENTER",
        splitByRow=True,
    )

    row_count = len(rows)

    #
    # Keep only small tables together.
    # Large tables should split naturally.
    #

    #
    # Small institutional tables should stay
    # together.
    #
    if row_count <= 8:

        table.keepTogether = True

    else:

        #
        # Large analytical tables should
        # split naturally.
        #
        table.keepTogether = False

    table.repeatRows = repeat_rows

    table.splitByRow = True

    #
    # Apply canonical institutional styling
    #

    table.setStyle(
        _default_table_style()
    )

    #
    # Table-specific overrides
    #

    table.setStyle(
        TableStyle(

            [

                #
                # Header
                #

                ("ALIGN", (0, 0), (-1, 0), "CENTER"),

                #
                # Body
                #

                ("ALIGN", (0, 1), (-1, -1), "CENTER"),

                #
                # Vertical Alignment
                #

                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                #
                # Padding
                #

                ("TOPPADDING", (0, 0), (-1, -1), 8),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

            ]

        )
    )

    table.spaceBefore = 2
    table.spaceAfter = 14

    #
    # The section builder already keeps
    # headings with tables.
    # Large tables may split naturally.
    #
    table.keepWithNext = False

    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            if isinstance(cell, (list, tuple)):
                raise TypeError(
                    f"Nested list detected at row {r}, column {c}."
            )

    return table


# ==========================================================
# GENERIC TABLE
# ==========================================================

def build_table(
    rows,
    col_widths=None,
):
    """
    Generic institutional table.

    Suitable for any two-dimensional dataset.
    """

    return _build_table(
        rows,
        col_widths=col_widths,
        h_align="CENTER",
    )


# ==========================================================
# METRIC TABLE
# ==========================================================

def build_metric_table(
    metrics,
    *,
    col_widths=None,
):
    """
    Standard two-column institutional metric table.

    Accepts either

        dict

    or

        list[list]
    """

    if isinstance(metrics, dict):

        rows = [["Metric", "Value"]]

        for key, value in metrics.items():

            rows.append(
                [
                    str(key),
                    str(value),
                ]
            )

    else:

        rows = metrics

    return _build_table(

        rows,

        col_widths=(

            col_widths

            if col_widths is not None

            else

            [

                CONTENT_WIDTH * 0.40,

                CONTENT_WIDTH * 0.60,

            ]

        ),

    )


# ==========================================================
# EXECUTIVE MATRIX
# ==========================================================

def build_executive_matrix(
    verdicts: dict,
):
    """
    Executive dashboard matrix.

    Used by

    - Executive Summary
    - Allocator Dashboard
    - Claim Dashboard
    """

    rows = [

        [

            "Assessment",

            "Result",

        ]

    ]

    for key, value in verdicts.items():

        rows.append(

            [

                str(key),

                str(value),

            ]

        )

    return _build_table(

        rows,

        col_widths=[

            CONTENT_WIDTH * 0.48,

            CONTENT_WIDTH * 0.52,

        ],

    )


# ==========================================================
# SUMMARY TABLE
# ==========================================================

def build_summary_table(
    rows,
):
    """
    Generic institutional summary table.

    Used for

    • Executive summaries

    • Score summaries

    • Report overviews
    """

    return _build_table(

        rows,

        col_widths=[

            CONTENT_WIDTH * 0.50,

            CONTENT_WIDTH * 0.50,

        ],

    )

# ==========================================================
# SCORE TABLE
# ==========================================================

def build_score_table(
    components,
):
    """
    Institutional score breakdown.

    Expected component interface:

        name
        earned_points
        maximum_points
        percentage
    """

    rows = [

        [

            "Component",

            "Score",

            "Maximum",

            "%",

        ]

    ]

    for component in components:

        rows.append(

            [

                component.name,

                component.earned_points,

                component.maximum_points,

                f"{component.percentage:.2f}%",

            ]

        )

    return _build_table(

        rows,

        col_widths=[

            3.0 * inch,

            1.0 * inch,

            1.0 * inch,

            0.8 * inch,

        ],

    )


# ==========================================================
# TIMELINE TABLE
# ==========================================================

def build_timeline_table(
    events,
):
    """
    Chronological event listing.

    Used by

    • Audit Report

    • Claim Lifecycle

    • Verification Timeline

    • Evidence History
    """

    rows = [

        [

            "Event",

            "Timestamp",

        ]

    ]

    rows.extend(events)

    return _build_table(

        rows,

        col_widths=[

            3.0 * inch,

            3.0 * inch,

        ],

    )


# ==========================================================
# COMPARISON TABLE
# ==========================================================

def build_comparison_table(
    headers,
    rows,
    col_widths=None,
):
    """
    Multi-column comparison table.

    Useful for

    • Claim comparisons

    • Before / After

    • Workspace comparisons

    • Portfolio comparisons
    """

    dataset = [

        headers,

    ]

    dataset.extend(rows)

    return _build_table(

        dataset,

        col_widths=col_widths,

    )


# ==========================================================
# MATRIX TABLE
# ==========================================================

def build_matrix_table(
    headers,
    rows,
    col_widths=None,
):
    """
    Generic institutional matrix.

    Suitable for any structured
    multi-column analytical data.
    """

    dataset = [

        headers,

    ]

    dataset.extend(rows)

    return _build_table(

        dataset,

        col_widths=col_widths,

    )


# ==========================================================
# STATUS HELPERS
# ==========================================================

def status_colour(
    status: str,
):
    """
    Return institutional colour
    associated with a status.
    """

    if status is None:

        return colors.black

    value = str(status).strip().lower()

    if value in {

        "verified",

        "valid",

        "approved",

        "passed",

        "strong",

        "institutional grade",

        "allocator ready",

    }:

        return TTL_GREEN

    if value in {

        "review",

        "monitoring",

        "moderate",

        "high review",

    }:

        return TTL_GREY

    if value in {

        "failed",

        "compromised",

        "rejected",

        "weak",

        "critical",

    }:

        return TTL_RED

    return colors.black


# ==========================================================
# TABLE STYLE HELPERS
# ==========================================================

def apply_status_colours(
    table,
    rows,
    status_column: int,
):
    """
    Apply semantic colours to a status column.

    Header row is skipped automatically.
    """

    style = []

    for index, row in enumerate(rows[1:], start=1):

        if len(row) <= status_column:

            continue

        style.append(

            (

                "TEXTCOLOR",

                (status_column, index),

                (status_column, index),

                status_colour(row[status_column]),

            )

        )

    if style:

        table.setStyle(

            TableStyle(style)

        )

    return table

# ==========================================================
# VALIDATION
# ==========================================================

def validate_table_rows(rows):
    """
    Basic validation for institutional tables.

    Ensures a non-empty iterable of rows is supplied.
    """

    if rows is None:
        raise ValueError("Table rows cannot be None.")

    if not isinstance(rows, (list, tuple)):
        raise TypeError(
            "Table rows must be a list or tuple."
        )

    if len(rows) == 0:
        raise ValueError(
            "Table must contain at least one row."
        )

    return rows


# ==========================================================
# EMPTY TABLE
# ==========================================================

def build_empty_table(
    message="No information available.",
):
    """
    Standard empty-state table.

    Used whenever a report has
    no data to display.
    """

    return _build_table(

        [

            [

                "Information",

            ],

            [

                message,

            ],

        ],

        col_widths=[

            6.0 * inch,

        ],

    )


# ==========================================================
# KEY / VALUE TABLE
# ==========================================================

def build_key_value_table(
    data: dict,
):
    """
    Convenience builder.

    Converts a dictionary into
    a two-column institutional table.
    """

    validate_table_rows(list(data.items()))

    rows = [

        [

            "Key",

            "Value",

        ]

    ]

    for key, value in data.items():

        rows.append(

            [

                str(key),

                str(value),

            ]

        )

    table = build_metric_table(rows)

    table.spaceBefore = 0
    table.spaceAfter = 8

    return table


# ==========================================================
# SCORECARD TABLE
# ==========================================================

def build_scorecard_table(
    title,
    score,
    band,
):
    """
    Compact executive scorecard.

    Primarily intended for
    executive summaries.
    """

    return _build_table(

        [

            [
                "Verification",
                "Score",
                "Classification",
            ],
            [
                title,
                score,
                band,
            ],

        ],

        col_widths=[

            CONTENT_WIDTH * 0.46,

            CONTENT_WIDTH * 0.20,

            CONTENT_WIDTH * 0.34,

        ],

    )


# ==========================================================
# FUTURE PLACEHOLDERS
# ==========================================================

#
# These builders intentionally exist as
# extension points for future reports.
#
# Examples:
#
# build_heatmap_table()
#
# build_distribution_table()
#
# build_evidence_matrix()
#
# build_allocator_matrix()
#
# build_trade_summary_table()
#
# build_portfolio_table()
#
# build_claim_matrix()
#
# build_audit_matrix()
#

# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    #
    # Generic
    #

    "build_table",

    "build_metric_table",

    "build_summary_table",

    "build_key_value_table",

    "build_empty_table",

    #
    # Executive
    #

    "build_executive_matrix",

    "build_scorecard_table",

    #
    # Analytics
    #

    "build_score_table",

    "build_matrix_table",

    "build_comparison_table",

    "build_timeline_table",

    #
    # Styling
    #

    "status_colour",

    "apply_status_colours",

]