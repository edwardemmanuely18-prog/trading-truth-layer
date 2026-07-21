"""
Trading Truth Layer

Volume IV

Domain Documentation Methodology

This module renders the institutional
documentation methodology used throughout
Volume IV of the Trading Truth Layer
Guidebook Series.
"""

from reportlab.platypus import (
    Paragraph,
    Spacer,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    SUBTITLE_STYLE,
    BODY_STYLE,
    BODY_CENTER_STYLE,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_documentation_methodology():

    """
    Builds the institutional Domain
    Documentation Methodology page
    for Volume IV.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN DOCUMENTATION METHODOLOGY",
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
            "The remaining sections of this Guidebook document "
            "each institutional subsystem independently.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Each subsystem is documented according to a common "
            "institutional methodology designed to provide "
            "consistent architectural documentation across the "
            "Trading Truth Layer ecosystem.",
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
    # DOCUMENTATION STANDARD
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOCUMENTATION STANDARD",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    documentation_questions = [

        "WHAT IS THE INFRASTRUCTURE?",

        "WHY DOES IT EXIST?",

        "WHICH INSTITUTIONAL PROBLEMS DOES IT SOLVE?",

        "WHICH OPERATIONAL COMPONENTS COMPRISE THE INFRASTRUCTURE?",

        "WHICH INSTITUTIONAL OUTPUTS ARE PRODUCED?",

        "HOW DOES IT INTERACT WITH THE BROADER TTL ECOSYSTEM?",

        "WHAT FUTURE INFRASTRUCTURE CAPABILITIES ARE PLANNED?",

        "ARCHITECTURE SUMMARY.",

    ]

    for index, question in enumerate(
        documentation_questions,
        start=1,
    ):

        story.append(
            Paragraph(
                f"{index}. {question}",
                BODY_STYLE,
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
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL POSITIONING
    # --------------------------------------------------

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "INSTITUTIONAL POSITIONING",
            SUBTITLE_STYLE,
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
            "Every institutional domain documented throughout "
            "Volume IV follows this common documentation standard.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "This methodology ensures that institutions, "
            "allocators, auditors and market participants can "
            "understand the responsibilities, capabilities and "
            "architectural positioning of every subsystem within "
            "Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Institutional consistency in documentation is "
            "essential for understanding how the broader "
            "institutional trust infrastructure operates across "
            "the entire Trading Truth Layer ecosystem.",
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
    # CLOSING STATEMENT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "This methodology provides a canonical institutional "
            "framework for documenting every infrastructure "
            "domain contained within Trading Truth Layer.",
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
    # PAGE BREAK
    # --------------------------------------------------

    story.append(
        PageBreak()
    )

    return story


# ==========================================================
# END OF FILE
# ==========================================================