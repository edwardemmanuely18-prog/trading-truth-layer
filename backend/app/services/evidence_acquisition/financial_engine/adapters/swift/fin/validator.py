"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT FIN Validation Engine
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from typing import List

from .bic import BICValidator
from .currency import CurrencyValidator
from .amount import AmountParser
from .dates import validate_date

from .message import FINMessage
from .field_parser import FINFieldCollection


# ============================================================================
# Result
# ============================================================================


@dataclass(slots=True)
class FINValidationResult:

    valid: bool = True

    errors: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    def error(self, message: str) -> None:

        self.valid = False

        self.errors.append(message)

    def warning(self, message: str) -> None:

        self.warnings.append(message)

    @property
    def successful(
        self,
    ) -> bool:

        return self.valid


    def raise_if_invalid(
        self,
    ) -> None:

        if not self.valid:

            raise ValueError(
                "\n".join(
                    self.errors,
                )
            )


# ============================================================================
# Validator
# ============================================================================


class FINValidator:

    def __init__(self):

        self.currency = CurrencyValidator()

        self.amount = AmountParser()

        self.bic = BICValidator()

    def validate_date(
        self,
        value: str,
    ) -> bool:

        return validate_date(value)

    def validate_currency(
        self,
        value: str,
    ) -> bool:

        return self.currency.validate(value)

    def validate_amount(
        self,
        value: str,
    ) -> bool:

        return self.amount.validate(value)

    def validate_bic(
        self,
        value: str,
    ) -> bool:

        return self.bic.validate(value)

    # ----------------------------------------------------------
    # Message Validation
    # ----------------------------------------------------------

    def validate_message(
        self,
        message: FINMessage,
    ) -> FINValidationResult:

        result = FINValidationResult()

        if message.basic_header is None:

            result.error(
                "Missing Block 1 (Basic Header)."
            )

        if message.application_header is None:

            result.error(
                "Missing Block 2 (Application Header)."
            )

        if message.text is None:

            result.error(
                "Missing Block 4 (Text Block)."
            )

        return result

    def validate_required_fields(
        self,
        fields: FINFieldCollection,
        required: list[str],
    ) -> FINValidationResult:

        result = FINValidationResult()

        for tag in required:

            if tag not in fields:

                result.error(
                    f"Missing FIN field :{tag}:"
                )

        return result

    def validate_mt103(
        self,
        fields: FINFieldCollection,
    ) -> FINValidationResult:

        return self.validate_required_fields(

            fields,

            [

                "20",

                "23B",

                "32A",

                "50K",

                "59",

                "71A",

            ],

        )

    def validate_mt202(
        self,
        fields: FINFieldCollection,
    ) -> FINValidationResult:

        return self.validate_required_fields(

            fields,

            [

                "20",

                "21",

                "32A",

                "58A",

            ],

        )

    def validate_mt700(
        self,
        fields: FINFieldCollection,
    ) -> FINValidationResult:

        return self.validate_required_fields(

            fields,

            [

                "20",

                "31C",

                "40A",

            ],

        )


__all__ = [

    "FINValidationResult",

    "FINValidator",

]