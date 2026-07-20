"""
Trading Truth Layer

Volume I Cover

Institutional cover page adapter for:

VOLUME I

THE FOUNDATIONS OF
TRADING TRUST INFRASTRUCTURE

All rendering responsibilities are delegated
to the canonical guidebook cover framework.
"""

from app.services.pdf.guidebooks.common.guidebook_cover import (
    build_guidebook_cover,
)

from app.services.pdf.guidebooks.common.guidebook_constants import (
    VOLUME_1_TITLE,
    TTL_SHORT_POSITIONING_STATEMENT,
    INSTITUTIONAL_WHITEPAPER,
)


# ==========================================================
# VOLUME I METADATA
# ==========================================================

VOLUME_NUMBER = 1

VOLUME_TITLE = VOLUME_1_TITLE

VOLUME_SUBTITLE = (
    TTL_SHORT_POSITIONING_STATEMENT
)

PUBLICATION_TYPE = (
    INSTITUTIONAL_WHITEPAPER
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_volume_1_cover():
    """
    Builds the canonical cover page for:

    Trading Truth Layer Guidebook Series

    Volume I

    The Foundations of Trading Trust Infrastructure.

    Returns
    -------
    list

        ReportLab flowables representing
        the complete Volume I cover page.
    """

    return build_guidebook_cover(
        volume_number=VOLUME_NUMBER,
        title=VOLUME_TITLE,
        subtitle=VOLUME_SUBTITLE,
        publication_type=PUBLICATION_TYPE,
    )


# ==========================================================
# END OF FILE
# ==========================================================