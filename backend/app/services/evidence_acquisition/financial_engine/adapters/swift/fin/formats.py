"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT FIN Format Definitions

Canonical ISO15022 field format specifications.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Final
from typing import Optional


# ============================================================================
# Format Definition
# ============================================================================


@dataclass(frozen=True, slots=True)
class FINFormat:
    """
    Canonical SWIFT field format.
    """

    specification: str

    description: str

    fixed_length: bool

    max_length: Optional[int]


# ============================================================================
# Common ISO15022 Formats
# ============================================================================

N6: Final = FINFormat(

    specification="6!n",

    description="Exactly 6 numeric characters",

    fixed_length=True,

    max_length=6,
)

N8: Final = FINFormat(

    specification="8!n",

    description="Exactly 8 numeric characters",

    fixed_length=True,

    max_length=8,
)

A3: Final = FINFormat(

    specification="3!a",

    description="Exactly 3 alphabetic characters",

    fixed_length=True,

    max_length=3,
)

X16: Final = FINFormat(

    specification="16x",

    description="Up to 16 SWIFT X characters",

    fixed_length=False,

    max_length=16,
)

X35: Final = FINFormat(

    specification="35x",

    description="Up to 35 SWIFT X characters",

    fixed_length=False,

    max_length=35,
)

CURRENCY_AMOUNT: Final = FINFormat(

    specification="3!a15d",

    description="Currency plus amount",

    fixed_length=False,

    max_length=18,
)


FORMATS: Final = {

    "6!n": N6,

    "8!n": N8,

    "3!a": A3,

    "16x": X16,

    "35x": X35,

    "3!a15d": CURRENCY_AMOUNT,
}


__all__ = [

    "FINFormat",

    "FORMATS",

]