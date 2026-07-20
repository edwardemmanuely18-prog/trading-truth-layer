"""
Trading Truth Layer

Volume III

Trading Verification Infrastructure

Verification Certificates
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


def build_verification_certificates():

    """
    Builds the Verification Certificates
    section for Volume III.
    """

    story = []

    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION CERTIFICATES",
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
            "Institutional trust should produce "
            "institutional artifacts.",
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
            "Trading Truth Layer produces "
            "Verification Certificates as the "
            "canonical institutional artifact "
            "representing the outcome of the "
            "institutional verification process.",
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
            "Verification Certificates provide "
            "institutions with an independently "
            "verifiable representation of the "
            "institutional trust posture of a "
            "trading record.",
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
    # PURPOSE
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

    purposes = [

        "Represent institutional verification outcomes.",

        "Communicate institutional trust posture.",

        "Communicate verification results.",

        "Support institutional due diligence.",

        "Support evidence-based capital allocation.",

        "Provide canonical institutional trust artifacts.",

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
    # INSTITUTIONAL VALUE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL VALUE",
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
            "Verification Certificates enable "
            "institutions to evaluate trading "
            "records using governed institutional "
            "trust artifacts rather than relying "
            "upon self-reported performance claims.",
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
            "The Verification Certificate becomes "
            "the canonical institutional output "
            "of the Trading Verification "
            "Infrastructure.",
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
    # QUESTIONS ANSWERED
    # --------------------------------------------------

    story.append(PageBreak())

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

        "Has institutional verification been completed?",

        "What is the institutional trust posture?",

        "Can institutions rely upon the verification outcome?",

        "Can the record support institutional review?",

        "Can the record support capital allocation decisions?",

        "Has institutional trust been independently established?",

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
            "Verification Certificates transform "
            "institutional verification into "
            "institutional trust artifacts.",
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
            "Institutional trust should be "
            "independently verifiable, "
            "institutionally governed and "
            "allocator ready.",
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