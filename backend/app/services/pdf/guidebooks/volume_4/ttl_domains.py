"""
Trading Truth Layer

Volume IV

TTL Institutional Domains

This module renders the institutional
domain architecture of Trading Truth
Layer for Volume IV of the Guidebook
Series.
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


def build_ttl_domains():

    """
    Builds the TTL Institutional Domains
    page for Volume IV.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TTL INSTITUTIONAL DOMAINS",
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
            "The Trading Truth Layer ecosystem is exposed "
            "through a set of institutional infrastructure "
            "subsystems referred to as domains.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Each domain is responsible for a specific "
            "operational, verification, governance or trust "
            "manufacturing function within the broader "
            "institutional trust lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Domains are not independent pages.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "They are institutional infrastructures designed "
            "to manufacture trust, preserve evidence, govern "
            "performance records and support institutional "
            "capital allocation decisions.",
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
    # DOMAIN REGISTRY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN REGISTRY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    domains = [

        "EXECUTIVE WORKSPACE INFRASTRUCTURE (DASHBOARD).",

        "INSTITUTIONAL EVIDENCE INFRASTRUCTURE (EVIDENCE INTAKE).",

        "CANONICAL EVIDENCE INFRASTRUCTURE (EVIDENCE REGISTRY).",

        "CLAIM INFRASTRUCTURE (CLAIM OPERATIONS).",

        "TRUST INTELLIGENCE INFRASTRUCTURE (TRUST INTELLIGENCE).",

        "INSTITUTIONAL INVESTIGATION INFRASTRUCTURE (INVESTIGATION CENTER).",

        "PUBLIC TRUST INFRASTRUCTURE (PUBLIC TRUST LAYER).",

        "WORKSPACE GOVERNANCE INFRASTRUCTURE (ADMINISTRATION).",

    ]

    for index, domain in enumerate(
        domains,
        start=1,
    ):

        story.append(
            Paragraph(
                f"{index}. {domain}",
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
            "Together these institutional domains form the "
            "operational and governance surface of Trading "
            "Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Each domain contributes independently to the "
            "institutional trust lifecycle while operating "
            "as part of a broader institutional capital "
            "allocation infrastructure.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Collectively, the domains documented throughout "
            "Volume IV establish the institutional trust "
            "infrastructure required for evidence-based "
            "capital allocation.",
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
            "The following sections document every "
            "institutional domain currently implemented "
            "within Trading Truth Layer.",
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