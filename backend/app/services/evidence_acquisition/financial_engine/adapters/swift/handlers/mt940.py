"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT940 Handler

Canonical Customer Statement Message protocol handler.
"""

from __future__ import annotations

from ..protocol_handler import SwiftProtocolHandler
from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator


# ============================================================================
# MT940 Handler
# ============================================================================


class MT940Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "940"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT940"
        ]

        # --------------------------------------------------------------
        # Mandatory Fields
        # --------------------------------------------------------------

        for tag in definition[
            "mandatory_fields"
        ]:

            fields.require(
                tag,
            )

        # --------------------------------------------------------------
        # Statement Validation
        # --------------------------------------------------------------

        opening_balance = fields.require(
            "60F",
        )

        closing_balance = fields.require(
            "62F",
        )

        account = fields.require(
            "25",
        )

        statement_number = fields.require(
            "28C",
        )

        reference = fields.require(
            "20",
        )

        if not reference.strip():

            raise ValueError(
                "Statement reference is empty."
            )

        if not account.strip():

            raise ValueError(
                "Account identification is empty."
            )

        if not statement_number.strip():

            raise ValueError(
                "Statement number is empty."
            )

        validator.validate_date(
            opening_balance[1:7],
        )

        validator.validate_currency(
            opening_balance[7:10],
        )

        validator.validate_amount(
            opening_balance[10:],
        )

        validator.validate_date(
            closing_balance[1:7],
        )

        validator.validate_currency(
            closing_balance[7:10],
        )

        validator.validate_amount(
            closing_balance[10:],
        )

        return {

            "message": message,

            "fields": fields,

            "protocol": definition,

            "message_type": definition[
                "message_type"
            ],

            "message_name": definition[
                "message_name"
            ],

            "asset_class": definition[
                "asset_class"
            ],

            "document_type": definition[
                "document_type"
            ],

            "evidence_type": definition[
                "evidence_type"
            ],

        }


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "MT940Handler",
]