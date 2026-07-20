"""
Trading Truth Layer

Verification Layers

This module introduces the institutional
verification layers that collectively
transform trading activity into
institutionally verifiable evidence.
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


def build_verification_layers():

    """
    Builds the Verification Layers page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE VERIFICATION LAYERS",
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
            "Institutional verification is not "
            "performed by a single component. "
            "It is the result of multiple "
            "infrastructure layers operating "
            "together throughout the verification "
            "ecosystem.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # VERIFICATION FLOW
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Evidence Infrastructure",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_SM)
    )

    story.append(
        Paragraph(
            "Transforms raw trading activity into "
            "canonical institutional evidence.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    story.append(
        Paragraph(
            "Verification Infrastructure",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_SM)
    )

    story.append(
        Paragraph(
            "Independently verifies trading "
            "records and governs the institutional "
            "claim lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    story.append(
        Paragraph(
            "Trust Infrastructure",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_SM)
    )

    story.append(
        Paragraph(
            "Generates institutional trust "
            "intelligence, investigations and "
            "public verification systems.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_MD)
    )

    story.append(
        Paragraph(
            "Institutional Infrastructure",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(1, SPACE_SM)
    )

    story.append(
        Paragraph(
            "Produces allocator-ready reports, "
            "due diligence outputs and capital "
            "allocation workflows.",
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
    # INSTITUTIONAL WORKFLOW
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading Activity → Evidence → "
            "Verification → Trust → Institutional "
            "Outputs",
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
            "Every institutional verification "
            "output produced by Trading Truth "
            "Layer is derived from this "
            "multi-layer infrastructure workflow.",
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
            "Verification is therefore an "
            "institutional process rather than "
            "a single metric or score.",
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