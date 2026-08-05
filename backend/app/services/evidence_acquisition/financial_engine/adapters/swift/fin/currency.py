"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

ISO4217 Currency Validation
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Final

# Common currencies supported by the Financial Engine.
# This registry can later be expanded to the complete ISO4217 list.

ISO4217: Final = frozenset({

    "USD",
    "EUR",
    "GBP",
    "CHF",
    "JPY",
    "CAD",
    "AUD",
    "NZD",
    "CNY",
    "HKD",
    "SGD",
    "SEK",
    "NOK",
    "DKK",
    "ZAR",
    "KES",
    "UGX",
    "TZS",

})


@dataclass(slots=True)
class CurrencyValidator:

    def validate(
        self,
        code: str,
    ) -> bool:

        return code.upper() in ISO4217


__all__ = [

    "ISO4217",

    "CurrencyValidator",

]