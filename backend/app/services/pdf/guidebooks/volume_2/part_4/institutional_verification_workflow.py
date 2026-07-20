"""
Trading Truth Layer

Institutional Verification Workflow

This module formally introduces the
complete institutional verification
workflow implemented throughout Trading
Truth Layer's Verification Infrastructure.

Institutional verification is the result
of multiple infrastructure layers, engines
and governance procedures operating
together.
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


def build_institutional_verification_workflow():

    """
    Builds the Institutional Verification
    Workflow page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE INSTITUTIONAL VERIFICATION WORKFLOW",
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
            "performed by a single algorithm, "
            "report or verification score.",
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
            "Institutional verification is the "
            "result of multiple institutional "
            "infrastructure components operating "
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
    # VERIFICATION ECOSYSTEM
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional verification is "
            "established through:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    components = [

        "Evidence Infrastructure.",

        "Verification Infrastructure.",

        "Integrity Infrastructure.",

        "Governance Infrastructure.",

        "Institutional workflows.",

        "Claim lifecycle governance.",

        "Institutional reporting systems.",

        "Verification intelligence systems.",

    ]

    for component in components:

        story.append(
            Paragraph(
                f"• {component}",
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

    story.append(PageBreak())

    # --------------------------------------------------
    # VERIFICATION OUTPUTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional verification produces:",
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

        "Governed institutional evidence.",

        "Allocator-ready verification outputs.",

        "Audit-ready evidence packages.",

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
    # INSTITUTIONAL POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional verification is not "
            "a feature of Trading Truth Layer.",
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
            "Institutional verification is an "
            "entire infrastructure ecosystem "
            "designed to establish evidence-based "
            "trust across global capital markets.",
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
            "Trading Truth Layer transforms "
            "trading activity into institutionally "
            "verified evidence capable of "
            "supporting institutional due diligence "
            "and evidence-based capital allocation.",
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