"""
Trading Truth Layer

Institutional Outputs

This module formally introduces the
institutional outputs produced by Trading
Truth Layer's Verification Infrastructure.

Verification Infrastructure exists to
produce allocator-ready institutional
evidence.
"""

from reportlab.platypus import (
    Paragraph,
    Spacer,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    BODY_STYLE,
    BODY_CENTER_STYLE,
    SPACE_SM,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_institutional_outputs():

    """
    Builds the Institutional Outputs page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL OUTPUTS",
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
    # INTRODUCTION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Verification Infrastructure exists "
            "to transform trading activity into "
            "allocator-ready institutional evidence.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The institutional value of Trading "
            "Truth Layer is ultimately expressed "
            "through the institutional outputs "
            "produced by its verification ecosystem.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL OUTPUTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Verification Infrastructure produces:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    outputs = [

        "Institutionally verified trading records.",

        "Verification certificates.",

        "Evidence packages.",

        "Verification intelligence.",

        "Governed institutional evidence.",

        "Allocator-ready verification reports.",

        "Audit-ready verification artifacts.",

        "Institutional trust intelligence.",

    ]

    for output in outputs:

        story.append(
            Paragraph(
                f"• {output}",
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
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional outputs represent the "
            "final product of the institutional "
            "verification workflow.",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Institutional capital allocation "
            "requires institutional evidence that "
            "can be independently trusted and "
            "institutionally reviewed.",
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
    # CONCLUSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Truth Layer produces "
            "institutional outputs designed "
            "for global allocators, auditors, "
            "investigators and institutional "
            "decision makers.",
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