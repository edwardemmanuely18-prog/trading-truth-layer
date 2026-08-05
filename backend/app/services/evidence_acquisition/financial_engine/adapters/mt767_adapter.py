"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT MT767 Adapter

Guarantee / Standby Letter of Credit Amendment Adapter.

This adapter orchestrates the shared SWIFT FIN infrastructure and
converts MT767 amendment messages into canonical financial evidence.

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


class MT767Adapter(FinancialAdapter):
    """
    SWIFT MT767 Adapter.

    Responsibilities
    ----------------
    • Acquire MT767 messages.
    • Parse FIN transport blocks.
    • Extract business fields.
    • Execute shared FIN validation.
    • Convert MT767 fields into canonical amendment evidence.

    The adapter intentionally contains no FIN parsing logic.
    """

    PROVIDER = "SWIFT"

    MESSAGE_TYPE = "MT767"

    DESCRIPTION = "Guarantee Amendment"

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
    # MT767 Amendment Mapping
    # ------------------------------------------------------------------

    def _build_evidence(
        self,
        *,
        fields,
        message,
    ):

        amendment_date = None

        currency = None

        amount = None

        amendment_amount = fields.get("32B")

        if amendment_amount:

            currency = amendment_amount[:3]

            amount = self._amount_parser.parse(
                amendment_amount[3:]
            )

        if fields.get("30"):

            amendment_date = parse_date(
                fields["30"]
            )

        return {

            "provider": self.provider,

            "message_type": self.message_type,

            "guarantee_reference": fields.get("20"),

            "related_reference": fields.get("21"),

            "amendment_number": fields.get("23"),

            "amendment_date": amendment_date,

            "currency": currency,

            "amount": amount,

            "applicant": fields.get("50"),

            "beneficiary": fields.get("59"),

            "issuing_bank": fields.get("52A"),

            "amendment_details": (
                fields.get("77A")
                or fields.get("77B")
                or fields.get("77C")
            ),

            "sender_to_receiver_information": fields.get("72"),

            "metadata": message.metadata,

        }