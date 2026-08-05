"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT747 Handler

Canonical Amendment to Reimbursement Authorization protocol handler.
"""

from __future__ import annotations

from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator
from ..protocol_handler import SwiftProtocolHandler


class MT747Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "747"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT747"
        ]

        for tag in definition[
            "mandatory_fields"
        ]:

            fields.require(tag)

        amendment_date = fields.get(
            "30",
        )

        if amendment_date:

            validator.validate_date(
                amendment_date,
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
    "MT747Handler",
]