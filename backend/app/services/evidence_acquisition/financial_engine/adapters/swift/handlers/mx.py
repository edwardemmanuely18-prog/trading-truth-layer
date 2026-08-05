"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

ISO20022 MX Handler

Canonical ISO20022 protocol handler.
"""

from __future__ import annotations

from ..protocol_handler import SwiftProtocolHandler
from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator


# ============================================================================
# MX Handler
# ============================================================================


class MXHandler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "MX"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MX"
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
        # ISO20022 Validation
        # --------------------------------------------------------------

        if message is None:

            raise ValueError(
                "ISO20022 message is missing."
            )

        if fields is None:

            raise ValueError(
                "ISO20022 message fields are missing."
            )

        # Reserved for future ISO20022 schema validation
        # (pacs.*, camt.*, pain.*, sese.*, auth.*, etc.)

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
    "MXHandler",
]