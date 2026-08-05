"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT750 Handler

Canonical Advice of Discrepancy protocol handler.
"""

from __future__ import annotations

from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator
from ..protocol_handler import SwiftProtocolHandler


class MT750Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "750"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT750"
        ]

        for tag in definition[
            "mandatory_fields"
        ]:

            fields.require(tag)

        amount = fields.get(
            "32B",
        )

        if amount:

            validator.validate_currency(
                amount[:3],
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
    "MT750Handler",
]