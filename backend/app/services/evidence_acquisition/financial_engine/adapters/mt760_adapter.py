"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

SWIFT MT760 Adapter

Institutional adapter responsible for acquiring evidence from
SWIFT FIN MT760 (Guarantee / Standby Letter of Credit) messages.

The adapter is intentionally thin. It orchestrates the shared
FIN infrastructure and converts validated MT760 messages into
canonical financial evidence.

All parsing, transport and validation responsibilities are
delegated to the shared SWIFT FIN modules.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from .base_adapter import FinancialAdapter

from .swift.fin.tokenizer import FINTokenizer
from .swift.fin.block_parser import FINBlockParser
from .swift.fin.field_parser import FINFieldParser
from .swift.fin.validator import FINValidator
from .swift.fin.amount import AmountParser
from .swift.fin.dates import parse_date


class MT760Adapter(FinancialAdapter):
    """
    SWIFT MT760 Adapter.

    Responsibilities
    ----------------
    • Acquire raw MT760 messages.
    • Parse FIN transport blocks.
    • Extract business fields.
    • Execute shared FIN validation.
    • Convert MT760 fields into canonical evidence.

    The adapter intentionally contains no protocol parsing logic.
    """

    PROVIDER = "SWIFT"

    MESSAGE_TYPE = "MT760"

    DESCRIPTION = "Guarantee / Standby Letter of Credit"

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
        """
        Acquire evidence from a raw MT760 message.

        Parameters
        ----------
        raw_message:
            Complete SWIFT FIN MT760 message.

        Returns
        -------
        list
            Canonical evidence objects.
        """

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
    # MT760 Evidence Mapping
    # ------------------------------------------------------------------

    def _build_evidence(
        self,
        *,
        fields,
        message,
    ):
        """
        Converts MT760 business fields into canonical evidence.

        Only MT760-specific field mapping belongs here.
        """

        currency = None

        amount = None

        value = fields.get("32B")

        if value:

            currency = value[:3]

            amount = self._amount_parser.parse(
                value[3:]
            )

        return {

            "provider": self.provider,

            "message_type": self.message_type,

            "guarantee_reference": fields.get("20"),

            "related_reference": fields.get("21"),

            "issue_date": parse_date(
                fields.get("30")
            )
            if fields.get("30")
            else None,

            "expiry_date": parse_date(
                fields.get("31D")
            )
            if fields.get("31D")
            else None,

            "currency": currency,

            "amount": amount,

            "applicant": fields.get("50"),

            "beneficiary": fields.get("59"),

            "issuing_bank": fields.get("52A"),

            "guarantee_text": fields.get("77C"),

            "metadata": message.metadata,

        }