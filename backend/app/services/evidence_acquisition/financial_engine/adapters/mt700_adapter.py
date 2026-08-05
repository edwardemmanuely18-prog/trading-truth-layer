"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT MT700 Adapter

Issue of Documentary Credit Adapter.

This adapter orchestrates the shared SWIFT FIN infrastructure and
converts MT700 documentary credit messages into canonical financial
evidence.

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


class MT700Adapter(FinancialAdapter):
    """
    SWIFT MT700 Adapter.

    Responsibilities
    ----------------
    • Acquire MT700 messages.
    • Parse FIN transport blocks.
    • Extract business fields.
    • Execute shared FIN validation.
    • Convert MT700 fields into canonical documentary credit evidence.
    """

    PROVIDER = "SWIFT"

    MESSAGE_TYPE = "MT700"

    DESCRIPTION = "Issue of Documentary Credit"

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
    # MT700 Documentary Credit Mapping
    # ------------------------------------------------------------------

    def _build_evidence(
        self,
        *,
        fields,
        message,
    ):

        issue_date = None
        expiry_date = None

        currency = None
        amount = None

        if fields.get("31C"):

            issue_date = parse_date(
                fields["31C"]
            )

        if fields.get("31D"):

            expiry_date = parse_date(
                fields["31D"][:6]
            )

        if fields.get("32B"):

            value = fields["32B"]

            currency = value[:3]

            amount = self._amount_parser.parse(
                value[3:]
            )

        return {

            "provider": self.provider,

            "message_type": self.message_type,

            "documentary_credit_number": fields.get("20"),

            "issue_date": issue_date,

            "expiry_date": expiry_date,

            "documentary_credit_type": fields.get("40A"),

            "currency": currency,

            "amount": amount,

            "applicant": fields.get("50"),

            "beneficiary": fields.get("59"),

            "place_of_taking_in_charge": fields.get("44A"),

            "port_of_loading": fields.get("44E"),

            "port_of_discharge": fields.get("44F"),

            "place_of_final_destination": fields.get("44B"),

            "latest_shipment_date": fields.get("44C"),

            "goods_description": fields.get("45A"),

            "documents_required": fields.get("46A"),

            "additional_conditions": fields.get("47A"),

            "charges": fields.get("71B"),

            "metadata": message.metadata,

        }