"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT760 Constants

Canonical constants and metadata for the MT760
Bank Guarantee adapter.
"""

from __future__ import annotations

from typing import Final
from typing import FrozenSet


# ============================================================================
# Provider
# ============================================================================

PROVIDER_NAME: Final = "SWIFT"

PROVIDER_DISPLAY_NAME: Final = "SWIFT Financial Network"

PROVIDER_VENDOR: Final = "SWIFT"

PROVIDER_DESCRIPTION: Final = (
    "SWIFT Financial Infrastructure Adapter"
)

MESSAGE_TYPE: Final = "MT760"

MESSAGE_NAME: Final = "Guarantee / Standby Letter of Credit"

MESSAGE_CATEGORY: Final = "Category 7"

VERSION: Final = "1.0"

PROVIDER_VERSION: Final = VERSION


# ============================================================================
# SWIFT
# ============================================================================

STANDARD: Final = "SWIFT FIN"

FORMAT: Final = "ISO 15022"

NETWORK: Final = "SWIFT"


# ============================================================================
# Supported Sequences
# ============================================================================

SEQUENCE_A: Final = "A"

SEQUENCE_B: Final = "B"

SUPPORTED_SEQUENCES: Final[FrozenSet[str]] = frozenset({

    SEQUENCE_A,

    SEQUENCE_B,

})


# ============================================================================
# Sequence Delimiters
# ============================================================================

SEQUENCE_A_START: Final = "15A"

SEQUENCE_B_START: Final = "15B"


# ============================================================================
# Supported Field Options
# ============================================================================

ISSUER_OPTIONS: Final[FrozenSet[str]] = frozenset({

    "52A",

    "52D",

})


# ============================================================================
# Mandatory Fields
# ============================================================================

MANDATORY_FIELDS: Final[FrozenSet[str]] = frozenset({

    "15A",

    "27",

    "22A",

    "15B",

    "20",

    "30",

    "22D",

    "40C",

    "23B",

    "32B",

    "59",

})


# ============================================================================
# Optional Fields
# ============================================================================

OPTIONAL_FIELDS: Final[FrozenSet[str]] = frozenset({

    "31E",

    "35G",

    "50",

    "51",

    "52A",

    "52D",

    "71D",

    "45C",

    "72Z",

    "23X",

})


# ============================================================================
# Parsing
# ============================================================================

FIELD_PREFIX: Final = ":"

FIELD_SEPARATOR: Final = ":"

LINE_SEPARATOR: Final = "\n"

ENCODING: Final = "utf-8"


# ============================================================================
# Validation
# ============================================================================

DATE_LENGTH: Final = 6

BIC_LENGTH: Final = 8

EXTENDED_BIC_LENGTH: Final = 11

ISO_CURRENCY_LENGTH: Final = 3


# ============================================================================
# Limits
# ============================================================================

MAX_FIELD_LENGTH: Final = 10000

MAX_MESSAGE_SIZE: Final = 500000

MAX_SEQUENCE_COUNT: Final = 10


# ============================================================================
# Evidence
# ============================================================================

EVIDENCE_TYPE: Final = "BANK_GUARANTEE"

ASSET_CLASS: Final = "TRADE_FINANCE"

DOCUMENT_TYPE: Final = "BANK_GUARANTEE"


# ============================================================================
# Provenance
# ============================================================================

PROVENANCE_PROVIDER: Final = "SWIFT"

PROVENANCE_STANDARD: Final = "ISO15022"

PROVENANCE_MESSAGE: Final = "MT760"


# ============================================================================
# SWIFT Message Registry
# ============================================================================

SWIFT_MESSAGE_DEFINITIONS: Final = {

    # ------------------------------------------------------------------
    # MT103
    # ------------------------------------------------------------------

    "MT103": {

        "message_type": "MT103",

        "message_name": "Customer Credit Transfer",

        "message_category": "Category 1",

        "evidence_type": "CUSTOMER_CREDIT_TRANSFER",

        "asset_class": "PAYMENTS",

        "document_type": "PAYMENT",

        "provenance_message": "MT103",

        "mandatory_fields": frozenset({

            "20",
            "23B",
            "32A",
            "50K",
            "59",
            "71A",

        }),

        "optional_fields": frozenset({

            "13C",
            "23E",
            "26T",
            "33B",
            "36",
            "51A",
            "52A",
            "53A",
            "54A",
            "55A",
            "56A",
            "57A",
            "70",
            "71F",
            "71G",
            "72",
            "77B",

        }),

        "supported_sequences": frozenset({"A"}),

    },

    # ------------------------------------------------------------------
    # MT202
    # ------------------------------------------------------------------

    "MT202": {

        "message_type": "MT202",

        "message_name": "General Financial Institution Transfer",

        "message_category": "Category 2",

        "evidence_type": "FINANCIAL_INSTITUTION_TRANSFER",

        "asset_class": "INTERBANK",

        "document_type": "INTERBANK_TRANSFER",

        "provenance_message": "MT202",

        "mandatory_fields": frozenset({

            "20",
            "21",
            "32A",
            "52A",
            "58A",

        }),

        "optional_fields": frozenset({

            "13C",
            "53A",
            "54A",
            "56A",
            "57A",
            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

    # ------------------------------------------------------------------
    # MT700
    # ------------------------------------------------------------------

    "MT700": {

        "message_type": "MT700",

        "message_name": "Issue of a Documentary Credit",

        "message_category": "Category 7",

        "evidence_type": "DOCUMENTARY_CREDIT",

        "asset_class": "TRADE_FINANCE",

        "document_type": "LETTER_OF_CREDIT",

        "provenance_message": "MT700",

        "mandatory_fields": frozenset({

            "20",

            "31C",

            "40A",

            "50",

            "59",

        }),

        "optional_fields": frozenset({

            "27",

            "31D",

            "32B",

            "39A",

            "39B",

            "39C",

            "41A",

            "42C",

            "42A",

            "42D",

            "43P",

            "43T",

            "44A",

            "44B",

            "44C",

            "44D",

            "45A",

            "46A",

            "47A",

            "71B",

            "48",

            "49",

            "57A",

            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MT707
    # ------------------------------------------------------------------

    "MT707": {

        "message_type": "MT707",

        "message_name": "Amendment to a Documentary Credit",

        "message_category": "Category 7",

        "evidence_type": "DOCUMENTARY_CREDIT_AMENDMENT",

        "asset_class": "TRADE_FINANCE",

        "document_type": "LETTER_OF_CREDIT_AMENDMENT",

        "provenance_message": "MT707",

        "mandatory_fields": frozenset({

            "20",

            "21",

            "31C",

        }),

        "optional_fields": frozenset({

            "26E",

            "30",

            "32B",

            "33B",

            "34B",

            "39A",

            "39B",

            "39C",

            "44A",

            "44B",

            "44C",

            "44D",

            "45A",

            "46A",

            "47A",

            "49",

            "71B",

            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MT710
    # ------------------------------------------------------------------

    "MT710": {

        "message_type": "MT710",

        "message_name": "Advice of a Third Bank's Documentary Credit",

        "message_category": "Category 7",

        "evidence_type": "DOCUMENTARY_CREDIT_ADVICE",

        "asset_class": "TRADE_FINANCE",

        "document_type": "LETTER_OF_CREDIT",

        "provenance_message": "MT710",

        "mandatory_fields": frozenset({

            "20",

            "21",

            "27",

            "40B",

        }),

        "optional_fields": frozenset({

            "31C",

            "31D",

            "32B",

            "50",

            "59",

            "71B",

            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MT720
    # ------------------------------------------------------------------

    "MT720": {

        "message_type": "MT720",

        "message_name": "Transfer of a Documentary Credit",

        "message_category": "Category 7",

        "evidence_type": "DOCUMENTARY_CREDIT_TRANSFER",

        "asset_class": "TRADE_FINANCE",

        "document_type": "LETTER_OF_CREDIT_TRANSFER",

        "provenance_message": "MT720",

        "mandatory_fields": frozenset({

            "20",

            "21",

            "32B",

            "59",

        }),

        "optional_fields": frozenset({

            "50",

            "71B",

            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MT742
    # ------------------------------------------------------------------

    "MT742": {

        "message_type": "MT742",

        "message_name": "Reimbursement Claim",

        "message_category": "Category 7",

        "evidence_type": "REIMBURSEMENT_CLAIM",

        "asset_class": "TRADE_FINANCE",

        "document_type": "REIMBURSEMENT",

        "provenance_message": "MT742",

        "mandatory_fields": frozenset({

            "20",

            "21",

            "32B",

        }),

        "optional_fields": frozenset({

            "52A",

            "53A",

            "54A",

            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MT747
    # ------------------------------------------------------------------

    "MT747": {

        "message_type": "MT747",

        "message_name": "Amendment to Reimbursement Authorization",

        "message_category": "Category 7",

        "evidence_type": "REIMBURSEMENT_AMENDMENT",

        "asset_class": "TRADE_FINANCE",

        "document_type": "REIMBURSEMENT",

        "provenance_message": "MT747",

        "mandatory_fields": frozenset({

            "20",

            "21",

        }),

        "optional_fields": frozenset({

            "30",

            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MT750
    # ------------------------------------------------------------------

    "MT750": {

        "message_type": "MT750",

        "message_name": "Advice of Discrepancy",

        "message_category": "Category 7",

        "evidence_type": "DOCUMENTARY_CREDIT_DISCREPANCY",

        "asset_class": "TRADE_FINANCE",

        "document_type": "LETTER_OF_CREDIT",

        "provenance_message": "MT750",

        "mandatory_fields": frozenset({

            "20",

            "21",

        }),

        "optional_fields": frozenset({

            "32B",

            "71B",

            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MT752
    # ------------------------------------------------------------------

    "MT752": {

        "message_type": "MT752",

        "message_name": "Authorization to Pay / Accept / Negotiate",

        "message_category": "Category 7",

        "evidence_type": "PAYMENT_AUTHORIZATION",

        "asset_class": "TRADE_FINANCE",

        "document_type": "LETTER_OF_CREDIT",

        "provenance_message": "MT752",

        "mandatory_fields": frozenset({

            "20",

            "21",

        }),

        "optional_fields": frozenset({

            "32B",

            "53A",

            "54A",

            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MT754
    # ------------------------------------------------------------------

    "MT754": {

        "message_type": "MT754",

        "message_name": "Advice of Payment",

        "message_category": "Category 7",

        "evidence_type": "PAYMENT_ADVICE",

        "asset_class": "TRADE_FINANCE",

        "document_type": "PAYMENT",

        "provenance_message": "MT754",

        "mandatory_fields": frozenset({

            "20",

            "21",

            "32B",

        }),

        "optional_fields": frozenset({

            "53A",

            "54A",

            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MT756
    # ------------------------------------------------------------------

    "MT756": {

        "message_type": "MT756",

        "message_name": "Advice of Reimbursement or Payment",

        "message_category": "Category 7",

        "evidence_type": "REIMBURSEMENT_ADVICE",

        "asset_class": "TRADE_FINANCE",

        "document_type": "REIMBURSEMENT",

        "provenance_message": "MT756",

        "mandatory_fields": frozenset({

            "20",

            "21",

            "32B",

        }),

        "optional_fields": frozenset({

            "52A",

            "53A",

            "54A",

            "72",

        }),

        "supported_sequences": frozenset({"A"}),

    },

    # ------------------------------------------------------------------
    # MT760
    # ------------------------------------------------------------------

    "MT760": {

        "message_type": "MT760",

        "message_name": "Guarantee / Standby Letter of Credit",

        "message_category": "Category 7",

        "evidence_type": "BANK_GUARANTEE",

        "asset_class": "TRADE_FINANCE",

        "document_type": "BANK_GUARANTEE",

        "provenance_message": "MT760",

        "mandatory_fields": frozenset({

            "15A",

            "27",

            "22A",

            "15B",

            "20",

            "30",

            "22D",

            "40C",

            "23B",

            "32B",

            "59",

        }),

        "optional_fields": frozenset({

            "31E",

            "35G",

            "50",

            "51",

            "52A",

            "52D",

            "71D",

            "45C",

            "72Z",

            "23X",

        }),

        "supported_sequences": SUPPORTED_SEQUENCES,

    },

    # ------------------------------------------------------------------
    # MT767
    # ------------------------------------------------------------------

    "MT767": {

        "message_type": "MT767",

        "message_name": "Guarantee Amendment",

        "message_category": "Category 7",

        "evidence_type": "BANK_GUARANTEE_AMENDMENT",

        "asset_class": "TRADE_FINANCE",

        "document_type": "BANK_GUARANTEE",

        "provenance_message": "MT767",

        "mandatory_fields": frozenset({

            "20",

            "21",

            "30",

        }),

        "optional_fields": frozenset({

            "22A",

            "26E",

            "31C",

            "72Z",

        }),

        "supported_sequences": SUPPORTED_SEQUENCES,

    },

        # ------------------------------------------------------------------
    # MT799
    # ------------------------------------------------------------------

    "MT799": {

        "message_type": "MT799",

        "message_name": "Free Format Message",

        "message_category": "Category 7",

        "evidence_type": "FREE_FORMAT_MESSAGE",

        "asset_class": "TRADE_FINANCE",

        "document_type": "FREE_FORMAT",

        "provenance_message": "MT799",

        "mandatory_fields": frozenset({

            "20",

        }),

        "optional_fields": frozenset({

            "21",

            "79",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MT940
    # ------------------------------------------------------------------

    "MT940": {

        "message_type": "MT940",

        "message_name": "Customer Statement",

        "message_category": "Category 9",

        "evidence_type": "BANK_STATEMENT",

        "asset_class": "CASH_MANAGEMENT",

        "document_type": "ACCOUNT_STATEMENT",

        "provenance_message": "MT940",

        "mandatory_fields": frozenset({

            "20",

            "25",

            "28C",

            "60F",

            "62F",

        }),

        "optional_fields": frozenset({

            "61",

            "86",

            "64",

            "65",

        }),

        "supported_sequences": frozenset({"A"}),

    },

        # ------------------------------------------------------------------
    # MX
    # ------------------------------------------------------------------

    "MX": {

        "message_type": "MX",

        "message_name": "ISO 20022 Financial Message",

        "message_category": "ISO20022",

        "evidence_type": "ISO20022_MESSAGE",

        "asset_class": "FINANCIAL_INFRASTRUCTURE",

        "document_type": "ISO20022",

        "provenance_message": "MX",

        "mandatory_fields": frozenset(),

        "optional_fields": frozenset(),

        "supported_sequences": frozenset(),

    },

}


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [

    "PROVIDER_NAME",

    "PROVIDER_DISPLAY_NAME",

    "PROVIDER_VENDOR",

    "PROVIDER_DESCRIPTION",

    "PROVIDER_VERSION",

    "MESSAGE_TYPE",

    "MESSAGE_NAME",

    "MESSAGE_CATEGORY",

    "VERSION",

    "STANDARD",

    "FORMAT",

    "NETWORK",

    "SEQUENCE_A",

    "SEQUENCE_B",

    "SUPPORTED_SEQUENCES",

    "SEQUENCE_A_START",

    "SEQUENCE_B_START",

    "ISSUER_OPTIONS",

    "MANDATORY_FIELDS",

    "OPTIONAL_FIELDS",

    "FIELD_PREFIX",

    "FIELD_SEPARATOR",

    "LINE_SEPARATOR",

    "ENCODING",

    "DATE_LENGTH",

    "BIC_LENGTH",

    "EXTENDED_BIC_LENGTH",

    "ISO_CURRENCY_LENGTH",

    "MAX_FIELD_LENGTH",

    "MAX_MESSAGE_SIZE",

    "MAX_SEQUENCE_COUNT",

    "EVIDENCE_TYPE",

    "ASSET_CLASS",

    "DOCUMENT_TYPE",

    "PROVENANCE_PROVIDER",

    "PROVENANCE_STANDARD",

    "PROVENANCE_MESSAGE",

    "SWIFT_MESSAGE_DEFINITIONS",
]