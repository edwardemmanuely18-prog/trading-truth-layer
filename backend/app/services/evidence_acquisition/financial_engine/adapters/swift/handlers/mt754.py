"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT754 Handler

Canonical Advice of Payment protocol handler.
"""

from __future__ import annotations

from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator
from ..protocol_handler import SwiftProtocolHandler


class MT754Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "754"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT754"
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

        for bic_tag in (
            "53A",
            "54A",
        ):

            bic = fields.get(
                bic_tag,
            )

            if bic:

                validator.validate_bic(
                    bic,
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
    "MT754Handler",
]