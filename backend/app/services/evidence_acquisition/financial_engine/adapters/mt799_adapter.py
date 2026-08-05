"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT MT799 Adapter

Free Format Banking Message Adapter.

This adapter orchestrates the shared SWIFT FIN infrastructure and
converts MT799 messages into canonical financial communication
evidence.

All FIN parsing, validation and transport responsibilities are
delegated to the shared FIN modules.
"""

from __future__ import annotations

from typing import Any

from .base_adapter import FinancialAdapter

from .swift.fin.block_parser import FINBlockParser
from .swift.fin.field_parser import FINFieldParser
from .swift.fin.tokenizer import FINTokenizer
from .swift.fin.validator import FINValidator


class MT799Adapter(FinancialAdapter):
    """
    SWIFT MT799 Adapter.

    Responsibilities
    ----------------
    • Acquire MT799 messages.
    • Parse FIN transport blocks.
    • Extract business fields.
    • Execute shared FIN validation.
    • Convert MT799 fields into canonical communication evidence.

    MT799 is intentionally free-format. The adapter preserves the
    business communication rather than attempting to infer unsupported
    financial semantics.
    """

    PROVIDER = "SWIFT"

    MESSAGE_TYPE = "MT799"

    DESCRIPTION = "Free Format Banking Message"

    def __init__(self) -> None:

        self._tokenizer = FINTokenizer()

        self._block_parser = FINBlockParser()

        self._field_parser = FINFieldParser()

        self._validator = FINValidator()

    # ------------------------------------------------------------------
    # Adapter Metadata
    # ------------------------------------------------------------------

    @property
    def provider(self) -> str:

        return self.PROVIDER

    @property
    def message_type(self) -> str:

        return self.MESSAGE_TYPE

    @property
    def description(self) -> str:

        return self.DESCRIPTION

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire(
        self,
        raw_message: str,
    ) -> list[Any]:

        fin_message = self._parse(raw_message)

        fields = self._extract_fields(fin_message)

        self._validate(fields)

        evidence = self._build_evidence(
            fields=fields,
            message=fin_message,
        )

        return [evidence]

    # ------------------------------------------------------------------
    # Shared FIN Pipeline
    # ------------------------------------------------------------------

    def _parse(
        self,
        raw_message: str,
    ):

        tokens = self._tokenizer.tokenize(
            raw_message
        )

        return self._block_parser.parse(
            tokens
        )

    def _extract_fields(
        self,
        fin_message,
    ):

        return self._field_parser.parse(
            fin_message.text.content
        )

    def _validate(
        self,
        fields,
    ) -> None:

        self._validator.validate(
            fields
        )

    # ------------------------------------------------------------------
    # MT799 Communication Mapping
    # ------------------------------------------------------------------

    def _build_evidence(
        self,
        *,
        fields,
        message,
    ):

        communication = (
            fields.get("79")
            or fields.get("77A")
            or fields.get("77B")
            or fields.get("77C")
        )

        return {

            "provider": self.provider,

            "message_type": self.message_type,

            "message_reference": fields.get("20"),

            "related_reference": fields.get("21"),

            "sender_to_receiver_information": fields.get("72"),

            "communication": communication,

            "raw_business_fields": fields,

            "metadata": message.metadata,

        }