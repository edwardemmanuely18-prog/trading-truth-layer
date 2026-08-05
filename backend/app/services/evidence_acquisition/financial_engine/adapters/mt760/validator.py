"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT760 Validator

Institutional validator for MT760 messages.

Responsibilities
----------------
• Required field validation
• Field format validation
• Sequence validation
• Structural validation

Business interpretation is intentionally excluded.
"""

from __future__ import annotations

import re

from dataclasses import dataclass
from dataclasses import field

from typing import List

from .fields import (
    MT760_FIELDS,
    MANDATORY_FIELDS,
)

from .message import (
    MT760Message,
)


# ============================================================================
# Validation Result
# ============================================================================


@dataclass(slots=True)
class MT760ValidationResult:
    """
    Result of MT760 validation.
    """

    valid: bool = True

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def add_error(
        self,
        message: str,
    ) -> None:

        self.valid = False

        self.errors.append(message)

    def add_warning(
        self,
        message: str,
    ) -> None:

        self.warnings.append(message)


# ============================================================================
# Validator
# ============================================================================


class MT760Validator:
    """
    Canonical MT760 validator.
    """

    DATE_PATTERN = re.compile(
        r"^\d{6}$"
    )

    CURRENCY_AMOUNT_PATTERN = re.compile(
        r"^[A-Z]{3}[0-9,\.]+$"
    )

    BIC_PATTERN = re.compile(
        r"^[A-Z0-9]{8}([A-Z0-9]{3})?$"
    )

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def validate(
        self,
        message: MT760Message,
    ) -> MT760ValidationResult:

        result = MT760ValidationResult()

        self._validate_required_fields(
            message,
            result,
        )

        self._validate_field_formats(
            message,
            result,
        )

        self._validate_sequences(
            message,
            result,
        )

        return result

    # ------------------------------------------------------------------
    # Required Fields
    # ------------------------------------------------------------------

    def _validate_required_fields(
        self,
        message: MT760Message,
        result: MT760ValidationResult,
    ) -> None:

        for tag in MANDATORY_FIELDS:

            if not message.exists(tag):

                result.add_error(

                    f"Missing mandatory field {tag}"
                )

    # ------------------------------------------------------------------
    # Formats
    # ------------------------------------------------------------------

    def _validate_field_formats(
        self,
        message: MT760Message,
        result: MT760ValidationResult,
    ) -> None:

        issue_date = message.value("30")

        if issue_date:

            if not self.DATE_PATTERN.match(
                issue_date
            ):

                result.add_error(

                    "Field 30 has invalid date format"
                )

        amount = message.value("32B")

        if amount:

            if not self.CURRENCY_AMOUNT_PATTERN.match(
                amount
            ):

                result.add_error(

                    "Field 32B has invalid amount format"
                )

        bic = (
            message.value("52A")
            or message.value("52D")
        )

        if bic:

            bic = bic.replace("\n", "")

            if not self.BIC_PATTERN.match(
                bic
            ):

                result.add_error(

                    "Issuer BIC is invalid"
                )

    # ------------------------------------------------------------------
    # Sequences
    # ------------------------------------------------------------------

    def _validate_sequences(
        self,
        message: MT760Message,
        result: MT760ValidationResult,
    ) -> None:

        if message.sequence_count == 0:

            result.add_error(

                "No MT760 sequences detected"
            )

        if not message.sequence("A"):

            result.add_warning(

                "Sequence A missing"
            )

        if not message.sequence("B"):

            result.add_warning(

                "Sequence B missing"
            )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def supported(
        tag: str,
    ) -> bool:

        return tag in MT760_FIELDS


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "MT760ValidationResult",

    "MT760Validator",
]