"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT MT103 Adapter

Customer Credit Transfer Adapter.

This adapter orchestrates the shared SWIFT FIN infrastructure and
converts MT103 messages into canonical payment evidence.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from .base_adapter import FinancialAdapter

from .swift.fin.amount import AmountParser
from .swift.fin.block_parser import FINBlockParser
from .swift.fin.dates import parse_date
from .swift.fin.field_parser import FINFieldParser
from .swift.fin.tokenizer import FINTokenizer
from .swift.fin.validator import FINValidator


class MT103Adapter(FinancialAdapter):

    PROVIDER = "SWIFT"

    MESSAGE_TYPE = "MT103"

    DESCRIPTION = "Customer Credit Transfer"

    def __init__(self) -> None:

        self._tokenizer = FINTokenizer()

        self._block_parser = FINBlockParser()

        self._field_parser = FINFieldParser()

        self._validator = FINValidator()

        self._amount_parser = AmountParser()

    @property
    def provider(self) -> str:

        return self.PROVIDER

    @property
    def message_type(self) -> str:

        return self.MESSAGE_TYPE

    @property
    def description(self) -> str:

        return self.DESCRIPTION

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

            value_date = parse_date(value[:6])

            currency = value[6:9]

            amount = self._amount_parser.parse(
                value[9:]
            )

        return {

            "provider": self.provider,

            "message_type": self.message_type,

            "transaction_reference": fields.get("20"),

            "bank_operation_code": fields.get("23B"),

            "value_date": value_date,

            "currency": currency,

            "amount": amount,

            "ordering_customer": (
                fields.get("50A")
                or fields.get("50F")
                or fields.get("50K")
            ),

            "ordering_institution": fields.get("52A"),

            "intermediary": fields.get("56A"),

            "account_with_institution": fields.get("57A"),

            "beneficiary": fields.get("59"),

            "remittance_information": fields.get("70"),

            "charges": fields.get("71A"),

            "metadata": message.metadata,

        }