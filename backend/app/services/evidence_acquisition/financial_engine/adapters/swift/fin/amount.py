"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT Amount Utilities
"""

from __future__ import annotations

from decimal import Decimal


class AmountParser:
    """
    Parses SWIFT amount fields.

    Example:

        1250,75
            ↓
        Decimal("1250.75")
    """

    def parse(
        self,
        value: str,
    ) -> Decimal:

        normalized = value.replace(",", ".")

        return Decimal(
            normalized
        )

    def validate(
        self,
        value: str,
    ) -> bool:

        try:

            self.parse(value)

            return True

        except Exception:

            return False


__all__ = [

    "AmountParser",

]