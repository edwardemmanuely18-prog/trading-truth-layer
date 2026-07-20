"""
Trading Truth Layer

The TTL Doctrine

This module formally establishes the
five foundational principles of Institutional
Trading Trust Infrastructure.

Every infrastructure component inside the
Trading Truth Layer ecosystem inherits from
these principles.
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
    SPACE_SM,
)

from app.services.pdf.guidebooks.common.guidebook_constants import (
    TTL_DOCTRINE,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_ttl_doctrine():

    """
    Builds the TTL Doctrine page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE TTL DOCTRINE",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    # --------------------------------------------------
    # INTRODUCTION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The Trading Truth Layer Doctrine "
            "formalizes the foundational principles "
            "required to establish Institutional "
            "Trading Trust Infrastructure.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_SM,
        )
    )

    story.append(
        Paragraph(
            "Every infrastructure component within "
            "the Trading Truth Layer ecosystem "
            "inherits from these institutional "
            "principles.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_SM,
        )
    )

    # --------------------------------------------------
    # THE FIVE FOUNDATIONAL PRINCIPLES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE FIVE FOUNDATIONAL PRINCIPLES",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_SM,
        )
    )

    for index, principle in enumerate(
        TTL_DOCTRINE,
        start=1,
    ):

        story.append(

            Paragraph(
                f"PRINCIPLE {index}",
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

            Paragraph(
                principle,
                BODY_CENTER_STYLE,
            )

        )

        story.append(
            Spacer(
                1,
                SPACE_SM / 2,
            )
        )

    # --------------------------------------------------
    # INSTITUTIONAL CONCLUSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The TTL Doctrine represents the "
            "philosophical and institutional "
            "foundation of Trading Truth Layer.",
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
            "Institutional trust is not a feature. "
            "It is infrastructure.",
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
            "Institutional Trading Trust "
            "Infrastructure exists to enable "
            "evidence-based capital allocation "
            "across global capital markets.",
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