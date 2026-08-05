"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT799 Handler

Canonical Free Format Message protocol handler.
"""

from __future__ import annotations

from ..protocol_handler import SwiftProtocolHandler
from ..constants import SWIFT_MESSAGE_DEFINITIONS
from ..fin.validator import FINValidator


# ============================================================================
# MT799 Handler
# ============================================================================


class MT799Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "799"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT799"
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
        # Free Format Message Validation
        # --------------------------------------------------------------

        reference = fields.require(
            "20",
        )

        if not reference.strip():

            raise ValueError(
                "Message reference is empty."
            )

        if "21" in fields:

            related_reference = fields.require(
                "21",
            )

            if not related_reference.strip():

                raise ValueError(
                    "Related reference is empty."
                )

        if "79" in fields:

            narrative = fields.require(
                "79",
            )

            if not narrative.strip():

                raise ValueError(
                    "Free format narrative is empty."
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


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "MT799Handler",
]