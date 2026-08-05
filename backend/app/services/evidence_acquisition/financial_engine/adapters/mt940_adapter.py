"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT MT940 Adapter

Customer Statement Message Adapter.

This adapter orchestrates the shared SWIFT FIN infrastructure and
converts MT940 account statements into canonical financial evidence.

Unlike most MT adapters, MT940 may produce multiple transaction
evidence records from a single statement.
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


class MT940Adapter(FinancialAdapter):
    """
    SWIFT MT940 Adapter.

    Responsibilities
    ----------------
    • Acquire MT940 statements.
    • Parse FIN transport blocks.
    • Extract statement fields.
    • Execute shared FIN validation.
    • Produce canonical statement evidence.

    MT940 is statement-oriented and may yield multiple transaction
    records from a single SWIFT message.
    """

    PROVIDER = "SWIFT"

    MESSAGE_TYPE = "MT940"

    DESCRIPTION = "Customer Statement Message"

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

        fields = self._extract_fields(
            fin_message
        )

        self._validate(fields)

        return self._build_evidence(
            fields=fields,
            message=fin_message,
        )

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
    # MT940 Statement Mapping
    # ------------------------------------------------------------------

    def _build_evidence(
        self,
        *,
        fields,
        message,
    ) -> list[Any]:

        statement = {

            "provider": self.provider,

            "message_type": self.message_type,

            "statement_reference": fields.get("20"),

            "account_identification": fields.get("25"),

            "statement_number": fields.get("28C"),

            "opening_balance": fields.get("60F"),

            "closing_balance": fields.get("62F"),

            "available_balance": fields.get("64"),

            "forward_available_balance": fields.get("65"),

            "transactions": [],

            "metadata": message.metadata,

        }

        transaction_lines = fields.get("61")

        narratives = fields.get("86")

        if transaction_lines:

            if not isinstance(transaction_lines, list):

                transaction_lines = [
                    transaction_lines
                ]

            if narratives and not isinstance(
                narratives,
                list,
            ):

                narratives = [
                    narratives
                ]

            for index, transaction in enumerate(
                transaction_lines
            ):

                narrative = None

                if (
                    narratives
                    and index < len(narratives)
                ):

                    narrative = narratives[index]

                statement["transactions"].append(

                    {

                        "transaction": transaction,

                        "narrative": narrative,

                    }

                )

        return [

            statement

        ]