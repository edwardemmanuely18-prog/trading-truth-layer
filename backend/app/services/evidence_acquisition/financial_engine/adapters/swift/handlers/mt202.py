"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT202 Handler
"""

from __future__ import annotations

from ..protocol_handler import SwiftProtocolHandler
from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator


class MT202Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "202"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT202"
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

        field32a = fields.require(
            "32A",
        )

        validator.validate_date(
            field32a[:6],
        )

        validator.validate_currency(
            field32a[6:9],
        )

        validator.validate_amount(

            field32a[9:],

        )

        validator.validate_bic(
            fields.require("52A"),
        )

        validator.validate_bic(
            fields.require("58A"),
        )

        # --------------------------------------------------------------
        # References
        # --------------------------------------------------------------

        fields.require(
            "20",
        )

        fields.require(
            "21",
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


__all__ = [
    "MT202Handler",
]