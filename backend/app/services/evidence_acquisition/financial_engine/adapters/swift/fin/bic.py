"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

ISO9362 Business Identifier Code (BIC) Validation
"""

from __future__ import annotations

import re


class BICValidator:
    """
    Validates ISO9362 BIC codes.
    """

    PATTERN = re.compile(

        r"^[A-Z]{4}"

        r"[A-Z]{2}"

        r"[A-Z0-9]{2}"

        r"([A-Z0-9]{3})?$"

    )

    def validate(
        self,
        bic: str,
    ) -> bool:

        bic = bic.strip().upper()

        return bool(

            self.PATTERN.match(

                bic

            )

        )


__all__ = [

    "BICValidator",

]