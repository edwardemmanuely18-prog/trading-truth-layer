"""
Trading Truth Layer

The Future of Verification

This module formally introduces the
future of institutional verification
infrastructure across global capital
markets.

Independent verification will become an
institutional requirement of evidence-based
capital allocation.
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


def build_the_future_of_verification():

    """
    Builds The Future of Verification page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE FUTURE OF VERIFICATION",
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
    # INSTITUTIONAL DECLARATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Global capital markets are rapidly "
            "transitioning toward evidence-based "
            "decision making.",
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
            "Institutional participants increasingly "
            "require independently verifiable "
            "evidence before allocating capital, "
            "conducting due diligence or establishing "
            "institutional trust.",
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
            "Verification Infrastructure will "
            "become a foundational requirement "
            "of modern capital markets.",
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
    # THE FUTURE OF VERIFICATION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The future of verification "
            "infrastructure includes:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    future_capabilities = [

        "Independently verifiable trading records.",

        "Allocator-ready verification standards.",

        "Institutional trust intelligence systems.",

        "Portable institutional evidence.",

        "Global verification networks.",

        "Evidence-based institutional due diligence.",

        "Verification-first capital allocation.",

        "Institutional trading trust infrastructure.",

    ]

    for capability in future_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
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
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # POSITIONING STATEMENT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The question is no longer whether "
            "verification infrastructure is needed.",
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
            "The question is how global capital "
            "markets will operate without it.",
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
    # INSTITUTIONAL CLOSING STATEMENT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The future of institutional trust "
            "is independently verifiable evidence.",
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