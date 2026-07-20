"""
Trading Truth Layer

Who Requires Institutional Trading Trust Infrastructure?

This module explains who benefits from
institutional trust infrastructure and why
institutional trust is relevant across global
capital markets.
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


def build_who_is_ttl_built_for():

    """
    Builds the institutional trust ecosystem page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHO REQUIRES INSTITUTIONAL TRUST INFRASTRUCTURE?",
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
    # INSTITUTIONAL NARRATIVE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional trust infrastructure is "
            "not designed for a single participant "
            "within global capital markets. Trust is "
            "a universal requirement of capital "
            "allocation.",
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
            "Every participant that depends upon "
            "trading performance records ultimately "
            "depends upon institutional trust.",
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
    # TRUST ECOSYSTEM
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional Trading Trust Infrastructure "
            "benefits:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    institutional_groups = [

        "• Individual and Professional Traders",

        (
            "• Capital Allocators<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;- Family Offices<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;- Institutional Investors<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;- Investment Committees"
        ),

        "• Asset Managers and Funds",

        (
            "• Service Providers<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;- Brokers<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;- Auditors<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;- Verification Providers"
        ),

        "• Capital Markets Infrastructure Participants",

        "• Global Capital Markets",

    ]

    for group in institutional_groups:

        story.append(

            Paragraph(
                group,
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
    # INSTITUTIONAL CONTEXT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Institutional trust infrastructure "
            "becomes increasingly important as "
            "capital allocation decisions become "
            "larger, more complex, and more "
            "institutionally governed.",
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
            "Trading Truth Layer was built for "
            "every institution, allocator, and "
            "market participant that requires "
            "evidence-based trust in trading "
            "performance.",
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
            "Institutional trust infrastructure "
            "benefits the entire capital allocation "
            "ecosystem.",
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