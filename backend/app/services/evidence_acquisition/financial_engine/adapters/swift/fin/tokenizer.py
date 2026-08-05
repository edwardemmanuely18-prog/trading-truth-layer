"""
Trading Truth Layer (TTL)

SWIFT FIN Tokenizer

Lexical tokenizer for SWIFT FIN messages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .constants import BLOCK_PREFIX, BLOCK_SUFFIX


# ============================================================================
# Token
# ============================================================================


@dataclass(slots=True, frozen=True)
class FINToken:
    """
    Lexical token.
    """

    identifier: str

    content: str


# ============================================================================
# Tokenizer
# ============================================================================


class FINTokenizer:
    """
    Tokenizes SWIFT FIN blocks.

    Example:

        {1:F01...}
        {2:I760...}
        {3:{108:ABC}}
        {4:
        :20:...
        -}
        {5:{CHK:...}}
    """

    def tokenize(
        self,
        message: str,
    ) -> Iterator[FINToken]:

        index = 0
        length = len(message)

        if not message.strip():
            return

        message = (
            message
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )

        while index < length:

            if message[index] != BLOCK_PREFIX:

                index += 1
                continue

            end = self._find_matching_brace(
                message,
                index,
            )

            if end == -1:
                break

            block = message[index + 1:end]

            if ":" in block:

                identifier, content = block.split(
                    ":",
                    1,
                )

                identifier = identifier.strip()

                content = content.strip()

                yield FINToken(
                    identifier=identifier,
                    content=content,
                )

            index = end + 1

    def tokens(
        self,
        message: str,
    ) -> list[FINToken]:
        """
        Materialize all tokens.
        """

        return list(
            self.tokenize(
                message,
            )
        )

    def token_count(
        self,
        message: str,
    ) -> int:
        """
        Count FIN blocks.
        """

        return len(
            self.tokens(
                message,
            )
        )

    def contains_block(
        self,
        message: str,
        identifier: str,
    ) -> bool:

        return any(
            token.identifier == identifier
            for token in self.tokenize(
                message,
            )
        )

    @staticmethod
    def _find_matching_brace(
        text: str,
        start: int,
    ) -> int:

        depth = 0

        for i in range(start, len(text)):

            if text[i] == "{":
                depth += 1

            elif text[i] == "}":

                depth -= 1

                if depth == 0:
                    return i

        return -1


__all__ = [
    "FINToken",
    "FINTokenizer",
]