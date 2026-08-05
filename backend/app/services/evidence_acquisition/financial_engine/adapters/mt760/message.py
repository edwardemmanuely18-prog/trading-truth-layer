"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT760 Message

Canonical MT760 message representation.

This object represents a parsed MT760 message before it is
translated into canonical Financial Engine evidence.

Responsibilities
----------------
• Preserve MT760 structure
• Store field values
• Organize sequences
• Provide convenient field access
• Support validation and normalization
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from typing import Dict
from typing import List
from typing import Optional
from typing import Any


# ============================================================================
# Field Value
# ============================================================================


@dataclass(slots=True)
class MT760FieldValue:
    """
    Represents a parsed MT760 field.
    """

    tag: str

    value: str

    sequence: str


# ============================================================================
# Sequence
# ============================================================================


@dataclass(slots=True)
class MT760Sequence:
    """
    Represents a MT760 sequence.
    """

    name: str

    fields: Dict[str, MT760FieldValue] = field(
        default_factory=dict
    )

    def add(
        self,
        field_value: MT760FieldValue,
    ) -> None:

        self.fields[
            field_value.tag
        ] = field_value

    def get(
        self,
        tag: str,
    ) -> Optional[MT760FieldValue]:

        return self.fields.get(tag)

    def exists(
        self,
        tag: str,
    ) -> bool:

        return tag in self.fields


# ============================================================================
# Message
# ============================================================================


@dataclass(slots=True)
class MT760Message:
    """
    Canonical parsed MT760 message.
    """

    sequences: Dict[
        str,
        MT760Sequence,
    ] = field(default_factory=dict)

    raw_message: str = ""

    parsed_at: datetime = field(
        default_factory=datetime.utcnow
    )

    # ------------------------------------------------------------------
    # Sequence Management
    # ------------------------------------------------------------------

    def add_sequence(
        self,
        sequence: MT760Sequence,
    ) -> None:

        self.sequences[
            sequence.name
        ] = sequence

    def sequence(
        self,
        name: str,
    ) -> Optional[MT760Sequence]:

        return self.sequences.get(name)

    # ------------------------------------------------------------------
    # Field Access
    # ------------------------------------------------------------------

    def field(
        self,
        tag: str,
    ) -> Optional[MT760FieldValue]:

        for sequence in self.sequences.values():

            field_value = sequence.get(tag)

            if field_value is not None:

                return field_value

        return None

    def value(
        self,
        tag: str,
    ) -> Optional[str]:

        field_value = self.field(tag)

        if field_value is None:

            return None

        return field_value.value

    def exists(
        self,
        tag: str,
    ) -> bool:

        return self.field(tag) is not None

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        result = {}

        for sequence in self.sequences.values():

            for field_value in sequence.fields.values():

                result[
                    field_value.tag
                ] = field_value.value

        return result

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def field_count(
        self,
    ) -> int:

        return sum(

            len(sequence.fields)

            for sequence in self.sequences.values()

        )

    @property
    def sequence_count(
        self,
    ) -> int:

        return len(self.sequences)


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "MT760FieldValue",

    "MT760Sequence",

    "MT760Message",
]