from __future__ import annotations

from reportlab.platypus import (
    KeepTogether,
    Spacer,
)

from reportlab.lib.units import mm


# ==========================================================
# Investigation Layout
# ==========================================================

#
# These helpers are intentionally Investigation-specific.
#
# They should NEVER be imported by the common PDF framework.
#


TOP_OF_PAGE_SPACER = 4 * mm

SECTION_SPACER = 2 * mm

DETAIL_SPACER = 1 * mm


def investigation_page_spacer():
    """
    Small spacer used before Investigation tables.

    This prevents tables from visually colliding with the
    institutional header divider without affecting the
    global document margins.
    """

    return Spacer(1, TOP_OF_PAGE_SPACER)


def investigation_section_spacer():
    """
    Standard spacing between Investigation components.
    """

    return Spacer(1, SECTION_SPACER)


def investigation_detail_spacer():
    """
    Compact spacing used inside Investigation cards.
    """

    return Spacer(1, DETAIL_SPACER)


def keep_investigation_block(*flowables):
    """
    Keep an Investigation heading together with the
    immediately following content whenever possible.

    This prevents titles being stranded at the bottom
    of a page while their table moves to the next page.
    """

    return KeepTogether(list(flowables))