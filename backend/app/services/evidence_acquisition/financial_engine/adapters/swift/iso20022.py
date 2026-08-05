"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT ISO 20022

Canonical ISO 20022 utilities shared by all SWIFT API clients.

Responsibilities
----------------
• ISO 20022 message classification
• Message metadata extraction
• Payload normalization
• Message family identification
• Common validation helpers

This module intentionally does NOT implement a complete ISO
20022 parser. Instead it provides a stable abstraction layer
between SWIFT payloads and the Financial Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from enum import Enum

from typing import Any
from typing import Dict
from typing import Optional


# ============================================================================
# Message Families
# ============================================================================


class ISO20022MessageFamily(str, Enum):

    CAMT = "camt"

    PACS = "pacs"

    PAIN = "pain"

    CAAA = "caaa"

    AUTH = "auth"

    REDA = "reda"

    TSMT = "tsmt"

    ACMT = "acmt"

    UNKNOWN = "unknown"


# ============================================================================
# Message Metadata
# ============================================================================


@dataclass(slots=True)
class ISO20022Metadata:
    """
    Canonical ISO 20022 metadata.
    """

    message_type: str

    family: ISO20022MessageFamily

    version: Optional[str] = None

    business_service: Optional[str] = None

    sender: Optional[str] = None

    receiver: Optional[str] = None

    creation_time: Optional[str] = None

    message_identifier: Optional[str] = None


# ============================================================================
# ISO Message
# ============================================================================


@dataclass(slots=True)
class ISO20022Message:
    """
    Canonical ISO message.
    """

    metadata: ISO20022Metadata

    payload: Dict[str, Any]

    raw_payload: Dict[str, Any]


# ============================================================================
# Classification
# ============================================================================


class ISO20022Classifier:

    """
    Identifies ISO 20022 message families.
    """

    FAMILY_PREFIXES = {

        "camt": ISO20022MessageFamily.CAMT,

        "pacs": ISO20022MessageFamily.PACS,

        "pain": ISO20022MessageFamily.PAIN,

        "caaa": ISO20022MessageFamily.CAAA,

        "auth": ISO20022MessageFamily.AUTH,

        "reda": ISO20022MessageFamily.REDA,

        "tsmt": ISO20022MessageFamily.TSMT,

        "acmt": ISO20022MessageFamily.ACMT,
    }

    @classmethod
    def classify(
        cls,
        message_type: str,
    ) -> ISO20022MessageFamily:

        prefix = message_type.split(".")[0].lower()

        return cls.FAMILY_PREFIXES.get(

            prefix,

            ISO20022MessageFamily.UNKNOWN,
        )


# ============================================================================
# Metadata Extraction
# ============================================================================


class ISO20022MetadataExtractor:

    """
    Extracts canonical metadata from ISO payloads.
    """

    @staticmethod
    def extract(
        payload: Dict[str, Any],
    ) -> ISO20022Metadata:

        message_type = payload.get(

            "message_type",

            "unknown",
        )

        return ISO20022Metadata(

            message_type=message_type,

            family=ISO20022Classifier.classify(
                message_type
            ),

            version=payload.get("version"),

            business_service=payload.get(
                "business_service"
            ),

            sender=payload.get("sender"),

            receiver=payload.get("receiver"),

            creation_time=payload.get(
                "creation_time"
            ),

            message_identifier=payload.get(
                "message_identifier"
            ),
        )


# ============================================================================
# Normalization
# ============================================================================


class ISO20022Normalizer:

    """
    Produces normalized ISO message objects.
    """

    @staticmethod
    def normalize(
        payload: Dict[str, Any],
    ) -> ISO20022Message:

        metadata = (
            ISO20022MetadataExtractor.extract(
                payload
            )
        )

        return ISO20022Message(

            metadata=metadata,

            payload=payload,

            raw_payload=payload,
        )


# ============================================================================
# Validation
# ============================================================================


class ISO20022Validator:

    """
    Lightweight validation helpers.
    """

    REQUIRED_FIELDS = (

        "message_type",
    )

    @classmethod
    def validate(
        cls,
        payload: Dict[str, Any],
    ) -> bool:

        return all(

            field in payload

            for field in cls.REQUIRED_FIELDS
        )


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "ISO20022MessageFamily",

    "ISO20022Metadata",

    "ISO20022Message",

    "ISO20022Classifier",

    "ISO20022MetadataExtractor",

    "ISO20022Normalizer",

    "ISO20022Validator",
]