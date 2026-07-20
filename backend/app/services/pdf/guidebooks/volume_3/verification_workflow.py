"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

Verification Workflow
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


# ==========================================================
# PUBLIC API
# ==========================================================


def build_verification_workflow():

    """
    Builds the Verification Workflow
    section for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION WORKFLOW",
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
            "Institutional trading verification "
            "is a governed workflow rather than "
            "a single verification event.",
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
            "Trading Truth Layer performs "
            "multiple institutional verification "
            "procedures before producing allocator-"
            "ready institutional trust artifacts.",
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
    # WORKFLOW
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL VERIFICATION WORKFLOW",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    workflow_steps = [

        "Institutional Evidence.",

        "Verification Metrics.",

        "Verification Analysis.",

        "Verification Bands.",

        "Verification Certificates.",

        "Institutional Outputs.",

        "Allocator-Ready Verification Records.",

    ]

    for step in workflow_steps:

        story.append(
            Paragraph(
                f"• {step}",
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_MD,
            )
        )

    # --------------------------------------------------
    # WORKFLOW EXPLANATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WORKFLOW EXPLANATION",
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
            "Institutional evidence enters the "
            "Trading Verification Infrastructure "
            "after evidence provenance and "
            "canonical trading records have "
            "already been established.",
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
        Paragraph(
            "The verification process evaluates "
            "multiple dimensions of institutional "
            "trust including evidence quality, "
            "integrity, governance and allocator "
            "readiness.",
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
        Paragraph(
            "Verification outcomes are then "
            "communicated through standardized "
            "institutional trust artifacts and "
            "institutional outputs.",
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
    # INSTITUTIONAL PURPOSE
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INSTITUTIONAL PURPOSE",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    purposes = [

        "Establish institutional trust.",

        "Evaluate verification readiness.",

        "Produce allocator-ready records.",

        "Generate institutional trust artifacts.",

        "Support evidence-based capital allocation.",

        "Standardize institutional verification outcomes.",

    ]

    for purpose in purposes:

        story.append(
            Paragraph(
                f"• {purpose}",
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_MD,
            )
        )

    # --------------------------------------------------
    # QUESTIONS ANSWERED
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL QUESTIONS ANSWERED",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    questions = [

        "Can the record be institutionally verified?",

        "Can institutional trust be established?",

        "Has verification been completed?",

        "Can allocators rely upon the verification outcome?",

        "Has allocator readiness been established?",

        "Can the record support institutional review?",

    ]

    for question in questions:

        story.append(
            Paragraph(
                f"• {question}",
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_MD,
            )
        )

    # --------------------------------------------------
    # POSITIONING STATEMENT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional verification is the "
            "process of transforming trading "
            "records into institutional trust "
            "artifacts.",
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
            "Verification Infrastructure exists "
            "to establish institutional trust "
            "before institutional capital is "
            "allocated.",
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