"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT707 Handler

Canonical Amendment to Documentary Credit protocol handler.
"""

from __future__ import annotations

from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator
from ..protocol_handler import SwiftProtocolHandler


class MT707Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "707"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT707"
        ]

        for tag in definition[
            "mandatory_fields"
        ]:

            fields.require(tag)

        validator.validate_date(
            fields.require("31C"),
        )

        amendment_number = fields.get(
            "26E",
        )

        if amendment_number is not None:

            amendment_number = amendment_number.strip()

            if not amendment_number:

                raise ValueError(
                    "Invalid amendment number."
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
    "MT707Handler",
]