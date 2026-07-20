"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

Verification Metrics
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


def build_verification_metrics():

    """
    Builds the Verification Metrics
    section for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION METRICS",
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
            "Trading Truth Layer evaluates "
            "institutional trust through multiple "
            "verification dimensions rather than "
            "through trading profitability alone.",
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
            "Every institutional trading record "
            "is evaluated using canonical "
            "verification metrics designed to "
            "measure evidence quality, governance, "
            "trustworthiness and institutional "
            "readiness.",
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
    # METRICS
    # --------------------------------------------------

    metrics = [

        (
            "Evidence Metric",
            "Evaluates the completeness and "
            "quality of the underlying trading "
            "evidence."
        ),

        (
            "Integrity Metric",
            "Evaluates whether institutional "
            "evidence integrity has been preserved "
            "throughout the verification lifecycle."
        ),

        (
            "Governance Metric",
            "Evaluates institutional governance "
            "requirements and lifecycle controls."
        ),

        (
            "Transparency Metric",
            "Evaluates institutional transparency "
            "and disclosure requirements."
        ),

        (
            "Stability Metric",
            "Evaluates the operational stability "
            "of the institutional trading record."
        ),

        (
            "Network Metric",
            "Evaluates institutional trust signals "
            "derived from the broader verification "
            "ecosystem."
        ),

        (
            "Review Metric",
            "Evaluates institutional review "
            "coverage and verification readiness."
        ),

        (
            "Dispute Metric",
            "Evaluates dispute records and "
            "institutional challenges associated "
            "with the trading record."
        ),

    ]

    for title, description in metrics:

        story.append(
            Paragraph(
                title,
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
                description,
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
    # INSTITUTIONAL PURPOSE
    # --------------------------------------------------

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

    story.append(
        Paragraph(
            "Verification metrics are designed "
            "to determine whether trading records "
            "can support institutional trust and "
            "evidence-based capital allocation.",
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

        "Can the trading evidence be trusted?",

        "Has institutional integrity been preserved?",

        "Can the record withstand institutional review?",

        "Is the record allocator ready?",

        "Can institutional capital rely upon the record?",

        "Does the record satisfy verification requirements?",

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
    # POSITIONING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Trading performance is only one "
            "component of institutional trust.",
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
            "Verification metrics exist to "
            "determine whether a trading record "
            "can be institutionally trusted, "
            "verified and reviewed.",
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