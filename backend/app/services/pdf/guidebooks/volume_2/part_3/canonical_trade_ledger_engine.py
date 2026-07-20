"""
Trading Truth Layer

Canonical Trade Ledger Engine

This module formally introduces the
Canonical Trade Ledger Engine and its
institutional responsibility as the
source of truth for trading evidence
within Trading Truth Layer.
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


def build_canonical_trade_ledger_engine():

    """
    Builds the Canonical Trade Ledger
    Engine page.
    """

    story = []

    # --------------------------------------------------
    # PAGE TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "THE CANONICAL TRADE LEDGER ENGINE",
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
            "Institutional verification requires "
            "a canonical source of truth.",
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
            "The Canonical Trade Ledger Engine is "
            "responsible for transforming acquired "
            "trading evidence into institutionally "
            "governed trading records.",
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
            "Every institutional verification "
            "workflow inside Trading Truth Layer "
            "operates upon the Canonical Trade "
            "Ledger rather than raw trading data.",
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
    # RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "The Canonical Trade Ledger Engine "
            "is responsible for:",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    responsibilities = [

        "Canonical trade record creation.",

        "Trade normalization.",

        "Institutional evidence preservation.",

        "Trade fingerprint generation.",

        "Historical trade lineage preservation.",

        "Institutional auditability.",

        "Institutional source-of-truth management.",

    ]

    for responsibility in responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
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
            "Institutional trust cannot be "
            "established upon fragmented records.",
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
            "Institutional trust requires a "
            "single canonical source of truth.",
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
            "The Canonical Trade Ledger represents "
            "that institutional source of truth "
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
    # CONCLUSION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "Verification Infrastructure operates "
            "upon canonical institutional records, "
            "not assumptions, screenshots or "
            "performance summaries.",
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