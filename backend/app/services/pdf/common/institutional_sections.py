from __future__ import annotations

"""
Trading Truth Layer
Institutional Section Framework

This module owns every reusable layout block used
throughout institutional reports.

Responsibilities

• Section layout
• Page break protection
• Narrative blocks
• Notices
• Callouts
• Findings
• Recommendations

No report should manually construct repeated
Paragraph + Spacer + KeepTogether layouts.
"""

from reportlab.platypus import (

    Paragraph,

    Spacer,

    KeepTogether,

    CondPageBreak,

)

from reportlab.lib.units import inch

from .institutional_theme import (

    SECTION_STYLE,

    SUBSECTION_STYLE,

    BODY_STYLE,

    NOTICE_STYLE,

    SPACE_SM,

    SPACE_MD,

    SPACE_LG,

)

# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _section_break():

    #
    # Ensure enough space remains for a section
    # heading and at least several lines of content.
    #

    return CondPageBreak(
        3.50 * inch,
    )


def _gap(height):

    """
    Standard spacer.
    """

    return Spacer(

        1,

        height,

    )


def _paragraph(

    text,

    style=BODY_STYLE,

):

    """
    Canonical paragraph builder.
    """

    return Paragraph(

        str(text),

        style,

    )

# ==========================================================
# SECTION TITLE
# ==========================================================

def build_section_title(
    title: str,
):
    """
    Canonical institutional section heading.

    Matches the Allocator Report style.

    Header
    --------------------------
    """

    return [

        _section_break(),

        _gap(SPACE_LG),

        _paragraph(
            title,
            SECTION_STYLE,
        ),

        _gap(SPACE_SM),

    ]


# ==========================================================
# SUBSECTION TITLE
# ==========================================================

def build_subsection_title(
    title: str,
):
    return [

        _paragraph(
            title,
            SUBSECTION_STYLE,
        ),

        _gap(
            SPACE_SM,
        ),

    ]


# ==========================================================
# NARRATIVE
# ==========================================================

def build_narrative(
    text,
):
    """
    Standard institutional narrative.

    Accepts either

        str

    or

        list[str]
    """

    if isinstance(text, str):

        paragraphs = [text]

    else:

        paragraphs = list(text)

    story = []

    for paragraph in paragraphs:

        story.append(
            _paragraph(
                paragraph,
                BODY_STYLE,
            )
        )

        story.append(
            _gap(
                SPACE_SM,
            )
        )

    return story


# ==========================================================
# NOTICE
# ==========================================================

def build_notice(
    text,
):
    """
    Institutional notice block.

    Used for

    • Verification notices

    • Allocator notes

    • Audit observations

    • Compliance notes
    """

    return [
        _paragraph(
            text,
            NOTICE_STYLE,
        ),
        _gap(
            SPACE_MD,
        ),
    ]

# ==========================================================
# METRIC BLOCK
# ==========================================================

def build_metric_block(
    title: str,
    table,
    narrative: str | None = None,
):
    """
    Canonical metric section.
    """

    story = []

    heading = build_subsection_title(title)

    story.append(_section_break())

    story.append(

        KeepTogether(

            [

                _gap(SPACE_MD),

                *heading,

                table,

            ]

        )

    )

    story.append(
        _gap(
            SPACE_MD,
        )
    )

    if narrative:

        story.extend(

            build_narrative(
                narrative,
            )

        )

    return story


# ==========================================================
# EXECUTIVE CALLOUT
# ==========================================================

def build_callout(
    title: str,
    text: str,
):

    story = []

    story.append(
        _section_break()
    )

    story.append(
        _gap(SPACE_MD)
    )

    story.append(

        KeepTogether(

            build_subsection_title(title)
            + [
                _paragraph(
                    text,
                    NOTICE_STYLE,
                )
            ]

        )

    )

    story.append(
        _gap(
            SPACE_MD,
        )
    )

    return story


# ==========================================================
# INTERNAL BULLET SECTION
# ==========================================================

def _build_bullet_section(
    title: str,
    items,
):
    """
    Canonical institutional bullet section.

    Used for findings, observations,
    recommendations and future bullet-based
    report sections.
    """

    story = []

    story.extend(
        build_subsection_title(
            title
        )
    )

    for item in items:

        story.append(
            _paragraph(
                f"\u2022 {item}",
                BODY_STYLE,
            )
        )

        story.append(
            _gap(
                SPACE_SM,
            )
        )

    return story


# ==========================================================
# FINDINGS
# ==========================================================

def build_findings(
    findings,
    *,
    title="Key Findings",
):
    """
    Canonical institutional findings.

    The title may be overridden by
    report modules while preserving
    consistent bullet formatting.
    """

    return _build_bullet_section(

        title,

        findings,

    )


# ==========================================================
# OBSERVATIONS
# ==========================================================

def build_observations(
    observations,
    *,
    title="Observations",
):
    """
    Canonical institutional observations.

    Allows report modules to provide
    chapter-specific headings while
    preserving presentation.
    """

    return _build_bullet_section(

        title,

        observations,

    )

# ==========================================================
# RECOMMENDATIONS
# ==========================================================

def build_recommendations(
    recommendations,
    *,
    title="Recommendations",
):
    """
    Institutional recommendations.

    Suitable for every report type.
    """

    story = []

    heading = build_subsection_title(
        title
    )

    items = []

    for recommendation in recommendations:

        items.append(

            _paragraph(
                f"• {recommendation}",
                BODY_STYLE,
            )

        )

        items.append(
            _gap(SPACE_SM)
        )

    story.append(

        KeepTogether(

            heading + items[:2]

        )

    )

    story.extend(
        items[2:]
    )

    return story

# ==========================================================
# SECTION GROUP
# ==========================================================

def build_section(
    title: str,
    content,
):

    story = []

    story.extend(
        build_section_title(title)
    )

    if isinstance(content, (list, tuple)):
        story.extend(content)
    else:
        story.append(content)

    story.append(
        _gap(
            SPACE_LG * 1.25,
        )
    )

    return story


# ==========================================================
# SECTION DIVIDER
# ==========================================================

def build_section_break():
    """
    Public wrapper for institutional
    page-break protection.
    """

    return _section_break()


# ==========================================================
# STANDARD GAP
# ==========================================================

def build_gap(
    size=SPACE_MD,
):
    """
    Canonical spacer.
    """

    return _gap(size)


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    #
    # Sections
    #

    "build_section",

    "build_section_title",

    "build_subsection_title",

    #
    # Narrative
    #

    "build_narrative",

    "build_notice",

    "build_callout",

    #
    # Analytics
    #

    "build_metric_block",

    #
    # Findings
    #

    "build_findings",

    "build_observations",

    "build_recommendations",

    #
    # Utilities
    #

    "build_gap",

    "build_section_break",

]