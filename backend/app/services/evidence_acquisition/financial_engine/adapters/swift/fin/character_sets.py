"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT FIN Character Sets
"""

from __future__ import annotations

import string


# ============================================================================
# Character Sets
# ============================================================================

SWIFT_X = set(

    string.ascii_uppercase +

    string.digits +

    "/-?:().,'+ "

)

SWIFT_Y = set(

    SWIFT_X |

    set("\n")
)

SWIFT_Z = set(

    SWIFT_Y |

    set("{}")
)


# ============================================================================
# Validator
# ============================================================================


def validate_character_set(

    value: str,

    allowed: set[str],

) -> bool:

    return all(

        c in allowed

        for c in value

    )


__all__ = [

    "SWIFT_X",

    "SWIFT_Y",

    "SWIFT_Z",

    "validate_character_set",

]