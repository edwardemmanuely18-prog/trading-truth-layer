"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT FIN Constants

Canonical constants shared by every SWIFT FIN message.
"""

from __future__ import annotations

from typing import Final, FrozenSet


# ============================================================================
# Standard
# ============================================================================

STANDARD: Final = "SWIFT FIN"

FORMAT: Final = "ISO 15022"

NETWORK: Final = "SWIFT"


# ============================================================================
# Blocks
# ============================================================================

BLOCK_1: Final = "1"

BLOCK_2: Final = "2"

BLOCK_3: Final = "3"

BLOCK_4: Final = "4"

BLOCK_5: Final = "5"


SUPPORTED_BLOCKS: Final[FrozenSet[str]] = frozenset({

    BLOCK_1,

    BLOCK_2,

    BLOCK_3,

    BLOCK_4,

    BLOCK_5,

})


# ============================================================================
# Message Categories
# ============================================================================

CATEGORY_1 = "Customer Payments"

CATEGORY_2 = "Financial Institution Transfers"

CATEGORY_3 = "Treasury"

CATEGORY_4 = "Collections"

CATEGORY_5 = "Securities"

CATEGORY_6 = "Precious Metals"

CATEGORY_7 = "Trade Finance"

CATEGORY_8 = "Travellers Cheques"

CATEGORY_9 = "Cash Management"


# ============================================================================
# Parsing
# ============================================================================

FIELD_PREFIX = ":"

BLOCK_PREFIX = "{"

BLOCK_SUFFIX = "}"

MESSAGE_TERMINATOR = "-}"

ENCODING = "utf-8"


# ============================================================================
# Limits
# ============================================================================

MAX_MESSAGE_SIZE = 5_000_000

MAX_FIELD_SIZE = 100_000

MAX_BLOCK_SIZE = 5_000_000


__all__ = [

    "STANDARD",

    "FORMAT",

    "NETWORK",

    "BLOCK_1",

    "BLOCK_2",

    "BLOCK_3",

    "BLOCK_4",

    "BLOCK_5",

    "SUPPORTED_BLOCKS",

    "CATEGORY_1",

    "CATEGORY_2",

    "CATEGORY_3",

    "CATEGORY_4",

    "CATEGORY_5",

    "CATEGORY_6",

    "CATEGORY_7",

    "CATEGORY_8",

    "CATEGORY_9",

    "FIELD_PREFIX",

    "BLOCK_PREFIX",

    "BLOCK_SUFFIX",

    "MESSAGE_TERMINATOR",

    "ENCODING",

    "MAX_MESSAGE_SIZE",

    "MAX_FIELD_SIZE",

    "MAX_BLOCK_SIZE",

]