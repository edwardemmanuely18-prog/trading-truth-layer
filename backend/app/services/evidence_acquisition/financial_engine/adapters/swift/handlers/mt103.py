"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT103 Protocol Handler

Canonical implementation of the MT103
Customer Credit Transfer protocol.
"""

from __future__ import annotations

from ..protocol_handler import (
    SwiftProtocolHandler,
)

from ..constants import (
    SWIFT_MESSAGE_DEFINITIONS,
)

from ..fin.validator import (
    FINValidator,
)


# ============================================================================
# MT103 Handler
# ============================================================================


class MT103Handler(
    SwiftProtocolHandler,
):

    @property
    def message_type(
        self,
    ) -> str:

        return "103"

    def process(
        self,
        adapter,
        message,
        fields,
    ) -> dict:

        validator = FINValidator()

        definition = SWIFT_MESSAGE_DEFINITIONS[
            "MT103"
        ]

        field32a = fields.require(
            "32A",
        )

        validator.validate_date(
            field32a[:6],
        )

        validator.validate_currency(
            field32a[6:9],
        )

        validator.validate_bic(
            fields.require("52A"),
        )

        validator.validate_bic(
            fields.require("57A"),
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
    "MT103Handler",
]