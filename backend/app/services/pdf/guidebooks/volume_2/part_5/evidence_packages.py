"""
Trading Truth Layer

Evidence Packages

This module formally introduces
Evidence Packages as institutional
deliverables produced by Trading Truth
Layer's Verification Infrastructure.

Evidence Packages are designed to deliver
institutionally governed trading evidence
to allocators, auditors and institutional
reviewers.
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


def build_evidence_packages():

    """
    Builds the Evidence Packages page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "EVIDENCE PACKAGES",
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
            "Institutional evidence should be "
            "portable, audit-ready and independently "
            "reviewable.",
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
            "Evidence Packages are institutional "
            "deliverables that consolidate the "
            "outputs of Trading Truth Layer's "
            "Verification Infrastructure.",
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
            "They provide allocators, auditors, "
            "investigators and institutional "
            "reviewers with governed institutional "
            "evidence suitable for independent "
            "evaluation.",
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
    # EVIDENCE PACKAGE COMPONENTS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Evidence Packages may include:",
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

        "Institutionally verified trading records.",

        "Verification certificates.",

        "Canonical trade ledger artifacts.",

        "Integrity assessment results.",

        "Governance assessment results.",

        "Historical audit records.",

        "Verification intelligence outputs.",

        "Allocator-ready institutional reports.",

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
    # INSTITUTIONAL VALUE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Evidence Packages are designed to "
            "support institutional due diligence "
            "procedures and evidence-based capital "
            "allocation decisions.",
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
            "Institutional evidence should not "
            "exist in isolated systems. It should "
            "be portable, governed and capable of "
            "independent institutional review.",
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
            "Evidence Packages enable institutional "
            "participants to independently assess "
            "the trustworthiness of trading records "
            "without relying upon subjective "
            "performance narratives.",
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
            "Institutional evidence should be "
            "allocator-ready, audit-ready and "
            "dispute-ready by design.",
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
            "Trading Truth Layer's Evidence "
            "Packages exist to make institutional "
            "trust portable across global capital "
            "markets.",
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