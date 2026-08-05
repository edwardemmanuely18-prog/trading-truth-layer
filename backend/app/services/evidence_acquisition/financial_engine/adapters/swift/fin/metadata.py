"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT FIN Metadata

Canonical metadata extracted from FIN headers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class FINMetadata:
    """
    Metadata describing a FIN message.
    """

    message_type: Optional[str] = None

    category: Optional[str] = None

    sender_bic: Optional[str] = None

    receiver_bic: Optional[str] = None

    direction: Optional[str] = None

    session_number: Optional[str] = None

    sequence_number: Optional[str] = None

    priority: Optional[str] = None

    service_identifier: Optional[str] = None

    message_reference: Optional[str] = None


__all__ = [
    "FINMetadata",
]