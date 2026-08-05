"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT760 Handler

Canonical Bank Guarantee protocol handler.
"""

from __future__ import annotations

from ..protocol_handler import SwiftProtocolHandler
from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator


class MT760Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "760"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT760"
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
        # Bank Guarantee Validation
        # --------------------------------------------------------------

        validator.validate_date(

            fields.require(
                "30",
            ),

        )

        validator.validate_currency(

            fields.require(
                "32B",
            )[:3],

        )

        validator.validate_amount(

            fields.require(
                "32B",
            )[3:],

        )

        beneficiary = fields.require(
            "59",
        )

        if not beneficiary.strip():

            raise ValueError(
                "Beneficiary field is empty."
            )

        guarantee_reference = fields.require(
            "20",
        )

        if not guarantee_reference.strip():

            raise ValueError(
                "Guarantee reference is empty."
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
    "MT760Handler",
]