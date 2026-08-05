"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT760 Normalizer

Transforms validated MT760 messages into provider-neutral
Financial Engine evidence.

Responsibilities
----------------
• Normalize MT760 fields
• Produce canonical evidence
• Remove SWIFT-specific semantics
• Preserve provenance
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import Optional

from .message import MT760Message


# ============================================================================
# Canonical Evidence
# ============================================================================


@dataclass(slots=True)
class BankGuaranteeEvidence:
    """
    Canonical representation of a bank guarantee.
    """

    reference: str

    issue_date: Optional[str]

    guarantee_type: Optional[str]

    applicable_rules: Optional[str]

    expiry_type: Optional[str]

    expiry_date: Optional[str]

    applicant: Optional[str]

    beneficiary: Optional[str]

    issuer: Optional[str]

    amount: Optional[str]

    currency: Optional[str]

    charges: Optional[str]

    presentation_conditions: Optional[str]

    provenance: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# Normalizer
# ============================================================================


class MT760Normalizer:
    """
    Canonical MT760 normalizer.
    """

    def normalize(
        self,
        message: MT760Message,
    ) -> BankGuaranteeEvidence:

        amount_field = message.value("32B")

        currency = None
        amount = None

        if amount_field:

            currency = amount_field[:3]

            amount = amount_field[3:]

        issuer = (
            message.value("52A")
            or
            message.value("52D")
        )

        evidence = BankGuaranteeEvidence(

            reference=message.value("20") or "",

            issue_date=message.value("30"),

            guarantee_type=message.value("22D"),

            applicable_rules=message.value("40C"),

            expiry_type=message.value("23B"),

            expiry_date=message.value("31E"),

            applicant=message.value("50"),

            beneficiary=message.value("59"),

            issuer=issuer,

            amount=amount,

            currency=currency,

            charges=message.value("71D"),

            presentation_conditions=message.value("45C"),

            provenance={

                "provider": "SWIFT",

                "message_type": "MT760",

                "reference": message.value("20"),

                "raw_fields": message.to_dict(),
            },
        )

        return evidence


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "BankGuaranteeEvidence",

    "MT760Normalizer",
]