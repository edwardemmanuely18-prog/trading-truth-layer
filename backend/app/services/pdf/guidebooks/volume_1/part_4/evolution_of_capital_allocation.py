"""
Trading Truth Layer

The Evolution of Capital Allocation

This module illustrates the institutional
evolution from trading performance to
evidence-based capital allocation.
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
    SPACE_MD,
    SPACE_LG,

)


def build_evolution_of_capital_allocation():

    story = []

    story.append(

        Paragraph(
            "THE EVOLUTION OF CAPITAL ALLOCATION",
            TITLE_STYLE,
        )

    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    story.append(

        Paragraph(
            "Historically, trading performance has "
            "been evaluated through isolated performance "
            "metrics and fragmented records.",
            BODY_STYLE,
        )

    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    evolution = [

        "Trading Performance",

        "↓",

        "Market Analytics",

        "↓",

        "Institutional Transparency",

        "↓",

        "Independent Verification",

        "↓",

        "Evidence-Based Trust",

        "↓",

        "Institutional Capital Allocation",

    ]

    for stage in evolution:

        story.append(

            Paragraph(
                stage,
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
        Spacer(
            1,
            SPACE_LG,
        )
    )

    story.append(

        Paragraph(
            "Trading Truth Layer establishes the "
            "institutional trust infrastructure "
            "required to enable this evolution "
            "within global capital markets.",
            BODY_STYLE,
        )

    )

    story.append(
        PageBreak()
    )

    return story