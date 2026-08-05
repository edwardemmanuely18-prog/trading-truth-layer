"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT MT202 Adapter

Financial Institution Transfer Adapter.

This adapter orchestrates the shared SWIFT FIN infrastructure and
converts MT202 messages into canonical interbank payment evidence.

All FIN parsing, validation and transport responsibilities are
delegated to the shared FIN modules.
"""

from __future__ import annotations

from typing import Any

from .base_adapter import FinancialAdapter

from .swift.fin.amount import AmountParser
from .swift.fin.block_parser import FINBlockParser
from .swift.fin.dates import parse_date
from .swift.fin.field_parser import FINFieldParser
from .swift.fin.tokenizer import FINTokenizer
from .swift.fin.validator import FINValidator


class MT202Adapter(FinancialAdapter):
    """
    SWIFT MT202 Adapter.

    Responsibilities
    ----------------
    • Acquire MT202 messages
    • Parse FIN blocks
    • Extract business fields
    • Execute shared FIN validation
    • Convert MT202 fields into canonical evidence

    The adapter intentionally contains no protocol parsing logic.
    """

    PROVIDER = "SWIFT"

    MESSAGE_TYPE = "MT202"

    DESCRIPTION = "Financial Institution Transfer"

    def __init__(self) -> None:

        self._tokenizer = FINTokenizer()

        self._block_parser = FINBlockParser()

        self._field_parser = FINFieldParser()

        self._validator = FINValidator()

        self._amount_parser = AmountParser()

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

        tokens = self._tokenizer.tokenize(raw_message)

        return self._block_parser.parse(tokens)

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

        self._validator.validate(fields)

    # ------------------------------------------------------------------
    # MT202 Evidence Mapping
    # ------------------------------------------------------------------

    def _build_evidence(
        self,
        *,
        fields,
        message,
    ):

        value_date = None
        currency = None
        amount = None

        value = fields.get("32A")

        if value:

            value_date = parse_date(
                value[:6]
            )

            currency = value[6:9]

            amount = self._amount_parser.parse(
                value[9:]
            )

        return {

            "provider": self.provider,

            "message_type": self.message_type,

            "transaction_reference": fields.get("20"),

            "related_reference": fields.get("21"),

            "value_date": value_date,

            "currency": currency,

            "amount": amount,

            "ordering_institution": fields.get("52A"),

            "sender_correspondent": fields.get("53A"),

            "receiver_correspondent": fields.get("54A"),

            "intermediary": fields.get("56A"),

            "account_with_institution": fields.get("57A"),

            "beneficiary_institution": fields.get("58A"),

            "sender_to_receiver_information": fields.get("72"),

            "metadata": message.metadata,

        }