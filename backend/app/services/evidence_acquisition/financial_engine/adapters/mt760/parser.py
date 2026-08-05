"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT760 Parser

Institutional parser for SWIFT MT760 messages.

Responsibilities
----------------
• Parse raw FIN messages
• Detect sequences
• Extract tagged fields
• Preserve multi-line field values
• Build canonical MT760Message

Validation and business interpretation are intentionally
handled by later pipeline stages.
"""

from __future__ import annotations

import re

from typing import List
from typing import Optional

from .fields import MT760_FIELDS
from .message import (
    MT760FieldValue,
    MT760Message,
    MT760Sequence,
)


# ============================================================================
# Parser
# ============================================================================


class MT760Parser:
    """
    Canonical MT760 parser.
    """

    FIELD_PATTERN = re.compile(
        r"^:(\d{2}[A-Z]?):(.*)$"
    )

    # ------------------------------------------------------------------
    # Parse
    # ------------------------------------------------------------------

    def parse(
        self,
        raw_message: str,
    ) -> MT760Message:

        message = MT760Message(
            raw_message=raw_message,
        )

        current_sequence: Optional[
            MT760Sequence
        ] = None

        current_tag: Optional[str] = None

        buffer: List[str] = []

        lines = raw_message.splitlines()

        for line in lines:

            match = self.FIELD_PATTERN.match(
                line
            )

            if match:

                self._flush_field(

                    message,

                    current_sequence,

                    current_tag,

                    buffer,
                )

                tag = match.group(1)

                value = match.group(2).strip()

                if tag.startswith("15"):

                    sequence_name = value or tag

                    current_sequence = MT760Sequence(
                        name=sequence_name,
                    )

                    message.add_sequence(
                        current_sequence
                    )

                current_tag = tag

                buffer = [value]

            else:

                buffer.append(
                    line.rstrip()
                )

        self._flush_field(

            message,

            current_sequence,

            current_tag,

            buffer,
        )

        return message

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _flush_field(

        self,

        message: MT760Message,

        sequence: Optional[
            MT760Sequence
        ],

        tag: Optional[str],

        buffer: List[str],
    ) -> None:

        if (
            sequence is None
            or tag is None
        ):

            return

        value = "\n".join(buffer).strip()

        field = MT760FieldValue(

            tag=tag,

            value=value,

            sequence=sequence.name,
        )

        sequence.add(field)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def supported(
        tag: str,
    ) -> bool:

        return tag in MT760_FIELDS
        

# ============================================================================
# Public Exports
# ============================================================================


__all__ = [
    "MT760Parser",
]