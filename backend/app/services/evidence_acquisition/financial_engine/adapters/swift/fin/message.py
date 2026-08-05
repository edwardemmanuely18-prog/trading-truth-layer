"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Canonical SWIFT FIN Message Model.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Optional

from .metadata import FINMetadata


# ============================================================================
# Base Block
# ============================================================================


@dataclass(slots=True)
class FINBlock:
    """
    Base FIN block.
    """

    identifier: str

    raw: str


# ============================================================================
# Block 1
# ============================================================================


@dataclass(slots=True)
class BasicHeaderBlock(FINBlock):

    application_id: Optional[str] = None

    service_id: Optional[str] = None

    logical_terminal: Optional[str] = None

    session_number: Optional[str] = None

    sequence_number: Optional[str] = None


# ============================================================================
# Block 2
# ============================================================================


@dataclass(slots=True)
class ApplicationHeaderBlock(FINBlock):

    input_output: Optional[str] = None

    message_type: Optional[str] = None

    destination: Optional[str] = None

    priority: Optional[str] = None


# ============================================================================
# Block 3
# ============================================================================


@dataclass(slots=True)
class UserHeaderBlock(FINBlock):

    fields: dict[str, str] = field(
        default_factory=dict
    )


# ============================================================================
# Block 4
# ============================================================================


@dataclass(slots=True)
class TextBlock(FINBlock):

    text: str = ""


# ============================================================================
# Block 5
# ============================================================================


@dataclass(slots=True)
class TrailerBlock(FINBlock):

    trailers: dict[str, str] = field(
        default_factory=dict
    )


# ============================================================================
# FIN Message
# ============================================================================


@dataclass(slots=True)
class FINMessage:
    """
    Canonical SWIFT FIN message.
    """

    raw_message: str

    basic_header: Optional[BasicHeaderBlock] = None

    application_header: Optional[ApplicationHeaderBlock] = None

    user_header: Optional[UserHeaderBlock] = None

    text: Optional[TextBlock] = None

    trailer: Optional[TrailerBlock] = None

    metadata: FINMetadata = field(
        default_factory=FINMetadata
    )

    parsed_at: datetime = field(
        default_factory=datetime.utcnow
    )

    # ------------------------------------------------------------------
    # Convenience Properties
    # ------------------------------------------------------------------

    @property
    def message_type(self) -> Optional[str]:
        """
        Return the FIN message type.
        """

        if self.application_header is None:
            return None

        return self.application_header.message_type

    @property
    def sender(self) -> Optional[str]:
        """
        Return the sending logical terminal.
        """

        if self.basic_header is None:
            return None

        return self.basic_header.logical_terminal

    @property
    def receiver(self) -> Optional[str]:
        """
        Return the destination logical terminal.
        """

        if self.application_header is None:
            return None

        return self.application_header.destination

    @property
    def has_user_header(self) -> bool:

        return self.user_header is not None

    @property
    def has_text_block(self) -> bool:

        return self.text is not None

    @property
    def has_trailer(self) -> bool:

        return self.trailer is not None


__all__ = [

    "FINBlock",

    "BasicHeaderBlock",

    "ApplicationHeaderBlock",

    "UserHeaderBlock",

    "TextBlock",

    "TrailerBlock",

    "FINMessage",

]