"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT700 Handler

Canonical Documentary Credit protocol handler.
"""

from __future__ import annotations

from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator
from ..protocol_handler import SwiftProtocolHandler


class MT700Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "700"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT700"
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
        # Documentary Credit Validation
        # --------------------------------------------------------------

        validator.validate_date(

            fields.require(
                "31C",
            ),

        )

        amount = fields.require(
            "32B",
        )

        validator.validate_currency(

            amount[:3],

        )

        applicant = fields.require(
            "50",
        )

        beneficiary = fields.require(
            "59",
        )

        if not applicant.strip():

            raise ValueError(
                "Applicant field is empty."
            )

        if not beneficiary.strip():

            raise ValueError(
                "Beneficiary field is empty."
            )

        issuing_bank = fields.get(
            "41A",
        )

        if issuing_bank:

            validator.validate_bic(
                issuing_bank,
            )

        reimbursing_bank = fields.get(
            "42A",
        )

        if reimbursing_bank:

            validator.validate_bic(
                reimbursing_bank,
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
    "MT700Handler",
]