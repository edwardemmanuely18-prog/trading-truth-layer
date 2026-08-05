"""
Trading Truth Layer (TTL)

SWIFT FIN Block Parser
"""

from __future__ import annotations

import re

from .message import (
    FINMessage,
    BasicHeaderBlock,
    ApplicationHeaderBlock,
    UserHeaderBlock,
    TextBlock,
    TrailerBlock,
)

from .tokenizer import FINTokenizer


class FINBlockParser:
    """
    Parses SWIFT FIN transport blocks into a structured
    FINMessage.
    """

    _BASIC_HEADER = re.compile(
        r"^(?P<application_id>.)(?P<service_id>.{2})(?P<logical_terminal>.{12})(?P<session_number>.{4})(?P<sequence_number>.{6})$"
    )

    _APPLICATION_INPUT = re.compile(
        r"^(?P<input_output>[IO])(?P<message_type>\d{3})(?P<destination>.{12})(?P<priority>.)?$"
    )

    def __init__(self):

        self.tokenizer = FINTokenizer()

    def parse(
        self,
        raw_message: str,
    ) -> FINMessage:

        message = FINMessage(
            raw_message=raw_message,
        )

        for token in self.tokenizer.tokenize(
            raw_message
        ):

            if token.identifier == "1":

                message.basic_header = self._parse_basic_header(
                    token.content,
                )

            elif token.identifier == "2":

                message.application_header = self._parse_application_header(
                    token.content,
                )

            elif token.identifier == "3":

                message.user_header = UserHeaderBlock(
                    identifier="3",
                    raw=token.content,
                )

            elif token.identifier == "4":

                message.text = TextBlock(
                    identifier="4",
                    raw=token.content,
                    text=token.content,
                )

            elif token.identifier == "5":

                message.trailer = TrailerBlock(
                    identifier="5",
                    raw=token.content,
                )

        return message

    # ------------------------------------------------------------------
    # Block 1
    # ------------------------------------------------------------------

    def _parse_basic_header(
        self,
        raw: str,
    ) -> BasicHeaderBlock:

        match = self._BASIC_HEADER.match(raw)

        if match is None:

            return BasicHeaderBlock(
                identifier="1",
                raw=raw,
            )

        return BasicHeaderBlock(

            identifier="1",

            raw=raw,

            application_id=match.group(
                "application_id",
            ),

            service_id=match.group(
                "service_id",
            ),

            logical_terminal=match.group(
                "logical_terminal",
            ),

            session_number=match.group(
                "session_number",
            ),

            sequence_number=match.group(
                "sequence_number",
            ),
        )

    # ------------------------------------------------------------------
    # Block 2
    # ------------------------------------------------------------------

    def _parse_application_header(
        self,
        raw: str,
    ) -> ApplicationHeaderBlock:

        match = self._APPLICATION_INPUT.match(
            raw,
        )

        if match is None:

            return ApplicationHeaderBlock(
                identifier="2",
                raw=raw,
            )

        return ApplicationHeaderBlock(

            identifier="2",

            raw=raw,

            input_output=match.group(
                "input_output",
            ),

            message_type=match.group(
                "message_type",
            ),

            destination=match.group(
                "destination",
            ),

            priority=match.group(
                "priority",
            ),
        )


__all__ = [
    "FINBlockParser",
]