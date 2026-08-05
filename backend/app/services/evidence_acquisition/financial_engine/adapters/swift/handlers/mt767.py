"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT767 Handler

Canonical Guarantee Amendment protocol handler.
"""

from __future__ import annotations

from ..protocol_handler import SwiftProtocolHandler
from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator


class MT767Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "767"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT767"
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
        # Guarantee Amendment Validation
        # --------------------------------------------------------------

        validator.validate_date(

            fields.require(
                "30",
            ),

        )

        amendment_reference = fields.require(
            "20",
        )

        if not amendment_reference.strip():

            raise ValueError(
                "Guarantee amendment reference is empty."
            )

        related_reference = fields.require(
            "21",
        )

        if not related_reference.strip():

            raise ValueError(
                "Related guarantee reference is empty."
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
    "MT767Handler",
]