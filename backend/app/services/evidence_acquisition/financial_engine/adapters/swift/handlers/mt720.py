"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT720 Handler

Canonical Transfer of Documentary Credit protocol handler.
"""

from __future__ import annotations

from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator
from ..protocol_handler import SwiftProtocolHandler


class MT720Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "720"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT720"
        ]

        for tag in definition[
            "mandatory_fields"
        ]:

            fields.require(tag)

        amount = fields.require(
            "32B",
        )

        validator.validate_currency(
            amount[:3],
        )

        beneficiary = fields.require(
            "59",
        )

        if not beneficiary.strip():

            raise ValueError(
                "Beneficiary field is empty."
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
    "MT720Handler",
]