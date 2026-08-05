"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Canonical Translators

Provider-specific financial objects are translated into canonical
Financial Engine evidence models before entering the synchronization
pipeline.
"""

from abc import ABC
from datetime import datetime
from typing import Any
from typing import Optional

from typing import Type

from dataclasses import dataclass
from dataclasses import field

from .models import (
    FinancialEvidencePackage,
    FinancialInstitution,
    FinancialAccount,
    CashBalanceEvidence,
    CashTransferEvidence,
    SettlementInstructionEvidence,
    SettlementConfirmationEvidence,
    CustodyHoldingEvidence,
    FundingEventEvidence,
    CorporateActionEvidence,
    BankStatementEvidence,
    LetterOfCreditEvidence,
    BankGuaranteeEvidence,
    CollateralEvidence,
    MarginEvidence,
    PaymentEvidence,
)


# ============================================================================
# Translation Accessor
# ============================================================================


class TranslationAccessor:
    """
    Safe access helpers used by every translation routine.
    """

    @staticmethod
    def as_string(data: Any, key: str) -> Optional[str]:
        if not isinstance(data, dict):
            return None

        value = data.get(key)

        if value is None:
            return None

        return str(value)

    @staticmethod
    def as_float(data: Any, key: str) -> Optional[float]:
        if not isinstance(data, dict):
            return None

        value = data.get(key)

        if value is None:
            return None

        try:
            return float(value)
        except Exception:
            return None

    @staticmethod
    def as_int(data: Any, key: str) -> Optional[int]:
        if not isinstance(data, dict):
            return None

        value = data.get(key)

        if value is None:
            return None

        try:
            return int(value)
        except Exception:
            return None

    @staticmethod
    def as_bool(data: Any, key: str) -> Optional[bool]:
        if not isinstance(data, dict):
            return None

        value = data.get(key)

        if value is None:
            return None

        return bool(value)

    @staticmethod
    def as_datetime(data: Any, key: str) -> Optional[datetime]:
        if not isinstance(data, dict):
            return None

        value = data.get(key)

        if isinstance(value, datetime):
            return value

        return None

    @staticmethod
    def as_list(value: Any):

        if value is None:
            return []

        return list(value)


# ============================================================================
# Financial Translator
# ============================================================================


class FinancialTranslator(ABC):
    """
    Canonical Financial Translator.

    Converts a normalized provider acquisition payload into a
    FinancialEvidencePackage.
    """

    provider_name = "financial"

    provider_version = "1.0"

    def translate(
        self,
        payload: dict,
    ) -> FinancialEvidencePackage:

        package = FinancialEvidencePackage()

        package.institution = self._translate_institution(
            payload.get("institution"),
        )

        package.account = self._translate_account(
            payload.get("account"),
        )

        package.cash_balances = self._translate_cash_balances(
            payload.get("cash_balances"),
        )

        package.cash_transfers = self._translate_cash_transfers(
            payload.get("cash_transfers"),
        )

        package.settlement_instructions = (
            self._translate_settlement_instructions(
                payload.get("settlement_instructions"),
            )
        )

        package.settlement_confirmations = (
            self._translate_settlement_confirmations(
                payload.get("settlement_confirmations"),
            )
        )

        package.custody_holdings = (
            self._translate_custody_holdings(
                payload.get("custody_holdings"),
            )
        )

        package.funding_events = self._translate_funding_events(
            payload.get("funding_events"),
        )

        package.corporate_actions = (
            self._translate_corporate_actions(
                payload.get("corporate_actions"),
            )
        )

        package.bank_statements = (
            self._translate_bank_statements(
                payload.get("bank_statements"),
            )
        )

        package.letters_of_credit = (
            self._translate_letters_of_credit(
                payload.get("letters_of_credit"),
            )
        )

        package.bank_guarantees = (
            self._translate_bank_guarantees(
                payload.get("bank_guarantees"),
            )
        )

        package.collateral = self._translate_collateral(
            payload.get("collateral"),
        )

        package.margin = self._translate_margin(
            payload.get("margin"),
        )

        package.payments = self._translate_payments(
            payload.get("payments"),
        )

        return package


    # ------------------------------------------------------------------
    # Infrastructure
    # ------------------------------------------------------------------

    def _translate_institution(
        self,
        value,
    ) -> Optional[FinancialInstitution]:

        if not value:
            return None

        return FinancialInstitution(

            institution_id=TranslationAccessor.as_string(
                value,
                "institution_id",
            ) or "",

            provider=value.get(
                "provider",
            ),

            legal_name=TranslationAccessor.as_string(
                value,
                "legal_name",
            ) or "",

            bic=TranslationAccessor.as_string(
                value,
                "bic",
            ),

            lei=TranslationAccessor.as_string(
                value,
                "lei",
            ),

            country=TranslationAccessor.as_string(
                value,
                "country",
            ),

            regulator=TranslationAccessor.as_string(
                value,
                "regulator",
            ),

            metadata=value.get(
                "metadata",
                {},
            ),
        )

    def _translate_account(
        self,
        value,
    ) -> Optional[FinancialAccount]:

        if not value:
            return None

        institution = self._translate_institution(
            value.get("institution"),
        )

        if institution is None:
            return None

        return FinancialAccount(

            account_id=TranslationAccessor.as_string(
                value,
                "account_id",
            ) or "",

            institution=institution,

            account_number=TranslationAccessor.as_string(
                value,
                "account_number",
            ) or "",

            account_name=TranslationAccessor.as_string(
                value,
                "account_name",
            ) or "",

            account_type=value.get(
                "account_type",
            ),

            currency=value.get(
                "currency",
            ),

            opened_at=TranslationAccessor.as_datetime(
                value,
                "opened_at",
            ),

            closed_at=TranslationAccessor.as_datetime(
                value,
                "closed_at",
            ),

            metadata=value.get(
                "metadata",
                {},
            ),
        )

    # ------------------------------------------------------------------
    # Financial Evidence
    # ------------------------------------------------------------------

    def _translate_cash_balances(
        self,
        values,
    ) -> list[CashBalanceEvidence]:

        balances: list[CashBalanceEvidence] = []

        for value in TranslationAccessor.as_list(values):

            balances.append(

                CashBalanceEvidence(

                    available_balance=value.get(
                        "available_balance",
                        0,
                    ),

                    ledger_balance=value.get(
                        "ledger_balance",
                        0,
                    ),

                    booked_balance=value.get(
                        "booked_balance",
                        0,
                    ),

                    pending_balance=value.get(
                        "pending_balance",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    value_date=TranslationAccessor.as_datetime(
                        value,
                        "value_date",
                    ),
                )
            )

        return balances

    def _translate_cash_transfers(
        self,
        values,
    ) -> list[CashTransferEvidence]:

        transfers: list[CashTransferEvidence] = []

        for value in TranslationAccessor.as_list(values):

            transfers.append(

                CashTransferEvidence(

                    transfer_reference=TranslationAccessor.as_string(
                        value,
                        "transfer_reference",
                    ) or "",

                    sender=value.get(
                        "sender",
                    ),

                    receiver=value.get(
                        "receiver",
                    ),

                    amount=value.get(
                        "amount",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    transfer_type=TranslationAccessor.as_string(
                        value,
                        "transfer_type",
                    ),

                    status=TranslationAccessor.as_string(
                        value,
                        "status",
                    ),

                    initiated_at=TranslationAccessor.as_datetime(
                        value,
                        "initiated_at",
                    ),

                    completed_at=TranslationAccessor.as_datetime(
                        value,
                        "completed_at",
                    ),
                )
            )

        return transfers

    def _translate_settlement_instructions(
        self,
        values,
    ) -> list[SettlementInstructionEvidence]:

        instructions: list[SettlementInstructionEvidence] = []

        for value in TranslationAccessor.as_list(values):

            instructions.append(

                SettlementInstructionEvidence(

                    instruction_id=TranslationAccessor.as_string(
                        value,
                        "instruction_id",
                    ) or "",

                    trade_reference=TranslationAccessor.as_string(
                        value,
                        "trade_reference",
                    ),

                    settlement_date=TranslationAccessor.as_datetime(
                        value,
                        "settlement_date",
                    ),

                    settlement_amount=value.get(
                        "settlement_amount",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    delivering_party=value.get(
                        "delivering_party",
                    ),

                    receiving_party=value.get(
                        "receiving_party",
                    ),

                    instruction_status=TranslationAccessor.as_string(
                        value,
                        "instruction_status",
                    ),
                )
            )

        return instructions

    def _translate_settlement_confirmations(
        self,
        values,
    ) -> list[SettlementConfirmationEvidence]:

        confirmations: list[
            SettlementConfirmationEvidence
        ] = []

        for value in TranslationAccessor.as_list(values):

            confirmations.append(

                SettlementConfirmationEvidence(

                    confirmation_id=TranslationAccessor.as_string(
                        value,
                        "confirmation_id",
                    ) or "",

                    instruction_reference=TranslationAccessor.as_string(
                        value,
                        "instruction_reference",
                    ),

                    settled_amount=value.get(
                        "settled_amount",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    settled_at=TranslationAccessor.as_datetime(
                        value,
                        "settled_at",
                    ),

                    settlement_status=TranslationAccessor.as_string(
                        value,
                        "settlement_status",
                    ),

                    settlement_location=TranslationAccessor.as_string(
                        value,
                        "settlement_location",
                    ),
                )
            )

        return confirmations

    def _translate_custody_holdings(
        self,
        values,
    ) -> list[CustodyHoldingEvidence]:

        holdings: list[
            CustodyHoldingEvidence
        ] = []

        for value in TranslationAccessor.as_list(values):

            holdings.append(

                CustodyHoldingEvidence(

                    security_id=TranslationAccessor.as_string(
                        value,
                        "security_id",
                    ) or "",

                    isin=TranslationAccessor.as_string(
                        value,
                        "isin",
                    ),

                    cusip=TranslationAccessor.as_string(
                        value,
                        "cusip",
                    ),

                    ticker=TranslationAccessor.as_string(
                        value,
                        "ticker",
                    ),

                    asset_name=TranslationAccessor.as_string(
                        value,
                        "asset_name",
                    ),

                    asset_type=TranslationAccessor.as_string(
                        value,
                        "asset_type",
                    ),

                    quantity=value.get(
                        "quantity",
                        0,
                    ),

                    market_value=value.get(
                        "market_value",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    valuation_date=TranslationAccessor.as_datetime(
                        value,
                        "valuation_date",
                    ),
                )
            )

        return holdings

    def _translate_funding_events(
        self,
        values,
    ) -> list[FundingEventEvidence]:

        events: list[
            FundingEventEvidence
        ] = []

        for value in TranslationAccessor.as_list(values):

            events.append(

                FundingEventEvidence(

                    funding_reference=TranslationAccessor.as_string(
                        value,
                        "funding_reference",
                    ) or "",

                    funding_type=TranslationAccessor.as_string(
                        value,
                        "funding_type",
                    ),

                    amount=value.get(
                        "amount",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    counterparty=value.get(
                        "counterparty",
                    ),

                    event_time=TranslationAccessor.as_datetime(
                        value,
                        "event_time",
                    ),

                    maturity_date=TranslationAccessor.as_datetime(
                        value,
                        "maturity_date",
                    ),
                )
            )

        return events

    def _translate_corporate_actions(
        self,
        values,
    ) -> list[CorporateActionEvidence]:

        actions: list[
            CorporateActionEvidence
        ] = []

        for value in TranslationAccessor.as_list(values):

            actions.append(

                CorporateActionEvidence(

                    corporate_action_id=TranslationAccessor.as_string(
                        value,
                        "corporate_action_id",
                    ) or "",

                    action_type=TranslationAccessor.as_string(
                        value,
                        "action_type",
                    ),

                    security_id=TranslationAccessor.as_string(
                        value,
                        "security_id",
                    ),

                    isin=TranslationAccessor.as_string(
                        value,
                        "isin",
                    ),

                    announcement_date=TranslationAccessor.as_datetime(
                        value,
                        "announcement_date",
                    ),

                    effective_date=TranslationAccessor.as_datetime(
                        value,
                        "effective_date",
                    ),

                    payable_date=TranslationAccessor.as_datetime(
                        value,
                        "payable_date",
                    ),

                    amount=value.get(
                        "amount",
                    ),

                    currency=value.get(
                        "currency",
                    ),
                )
            )

        return actions

    def _translate_bank_statements(
        self,
        values,
    ) -> list[BankStatementEvidence]:

        statements: list[
            BankStatementEvidence
        ] = []

        for value in TranslationAccessor.as_list(values):

            statements.append(

                BankStatementEvidence(

                    statement_reference=TranslationAccessor.as_string(
                        value,
                        "statement_reference",
                    ) or "",

                    statement_number=TranslationAccessor.as_string(
                        value,
                        "statement_number",
                    ),

                    period_start=TranslationAccessor.as_datetime(
                        value,
                        "period_start",
                    ),

                    period_end=TranslationAccessor.as_datetime(
                        value,
                        "period_end",
                    ),

                    opening_balance=value.get(
                        "opening_balance",
                        0,
                    ),

                    closing_balance=value.get(
                        "closing_balance",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),
                )
            )

        return statements

    def _translate_letters_of_credit(
        self,
        values,
    ) -> list[LetterOfCreditEvidence]:

        letters: list[
            LetterOfCreditEvidence
        ] = []

        for value in TranslationAccessor.as_list(values):

            letters.append(

                LetterOfCreditEvidence(

                    lc_reference=TranslationAccessor.as_string(
                        value,
                        "lc_reference",
                    ) or "",

                    applicant=value.get(
                        "applicant",
                    ),

                    beneficiary=value.get(
                        "beneficiary",
                    ),

                    issuing_bank=value.get(
                        "issuing_bank",
                    ),

                    advising_bank=value.get(
                        "advising_bank",
                    ),

                    amount=value.get(
                        "amount",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    expiry_date=TranslationAccessor.as_datetime(
                        value,
                        "expiry_date",
                    ),

                    issue_date=TranslationAccessor.as_datetime(
                        value,
                        "issue_date",
                    ),
                )
            )

        return letters

    def _translate_bank_guarantees(
        self,
        values,
    ) -> list[BankGuaranteeEvidence]:

        guarantees: list[
            BankGuaranteeEvidence
        ] = []

        for value in TranslationAccessor.as_list(values):

            guarantees.append(

                BankGuaranteeEvidence(

                    guarantee_reference=TranslationAccessor.as_string(
                        value,
                        "guarantee_reference",
                    ) or "",

                    guarantor=value.get(
                        "guarantor",
                    ),

                    beneficiary=value.get(
                        "beneficiary",
                    ),

                    applicant=value.get(
                        "applicant",
                    ),

                    guarantee_amount=value.get(
                        "guarantee_amount",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    issue_date=TranslationAccessor.as_datetime(
                        value,
                        "issue_date",
                    ),

                    expiry_date=TranslationAccessor.as_datetime(
                        value,
                        "expiry_date",
                    ),

                    guarantee_status=TranslationAccessor.as_string(
                        value,
                        "guarantee_status",
                    ),
                )
            )

        return guarantees

    def _translate_collateral(
        self,
        values,
    ) -> list[CollateralEvidence]:

        collateral: list[
            CollateralEvidence
        ] = []

        for value in TranslationAccessor.as_list(values):

            collateral.append(

                CollateralEvidence(

                    collateral_id=TranslationAccessor.as_string(
                        value,
                        "collateral_id",
                    ) or "",

                    collateral_type=TranslationAccessor.as_string(
                        value,
                        "collateral_type",
                    ),

                    asset_identifier=TranslationAccessor.as_string(
                        value,
                        "asset_identifier",
                    ),

                    quantity=value.get(
                        "quantity",
                        0,
                    ),

                    market_value=value.get(
                        "market_value",
                        0,
                    ),

                    haircut=value.get(
                        "haircut",
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    counterparty=value.get(
                        "counterparty",
                    ),

                    valuation_date=TranslationAccessor.as_datetime(
                        value,
                        "valuation_date",
                    ),
                )
            )

        return collateral

    def _translate_margin(
        self,
        values,
    ) -> list[MarginEvidence]:

        margins: list[
            MarginEvidence
        ] = []

        for value in TranslationAccessor.as_list(values):

            margins.append(

                MarginEvidence(

                    margin_id=TranslationAccessor.as_string(
                        value,
                        "margin_id",
                    ) or "",

                    margin_type=TranslationAccessor.as_string(
                        value,
                        "margin_type",
                    ),

                    required_margin=value.get(
                        "required_margin",
                        0,
                    ),

                    posted_margin=value.get(
                        "posted_margin",
                        0,
                    ),

                    excess_margin=value.get(
                        "excess_margin",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    valuation_date=TranslationAccessor.as_datetime(
                        value,
                        "valuation_date",
                    ),
                )
            )

        return margins

    def _translate_payments(
        self,
        values,
    ) -> list[PaymentEvidence]:

        payments: list[
            PaymentEvidence
        ] = []

        for value in TranslationAccessor.as_list(values):

            payments.append(

                PaymentEvidence(

                    payment_reference=TranslationAccessor.as_string(
                        value,
                        "payment_reference",
                    ) or "",

                    payment_method=TranslationAccessor.as_string(
                        value,
                        "payment_method",
                    ),

                    payer=value.get(
                        "payer",
                    ),

                    beneficiary=value.get(
                        "beneficiary",
                    ),

                    amount=value.get(
                        "amount",
                        0,
                    ),

                    currency=value.get(
                        "currency",
                    ),

                    execution_date=TranslationAccessor.as_datetime(
                        value,
                        "execution_date",
                    ),

                    payment_status=TranslationAccessor.as_string(
                        value,
                        "payment_status",
                    ),
                )
            )

        return payments


# ============================================================================
# Translation Result
# ============================================================================

from dataclasses import dataclass, field
from typing import Type


@dataclass(slots=True)
class TranslationResult:
    """
    Result returned by the TranslationService.
    """

    translated: bool = False

    evidence: FinancialEvidencePackage | None = None

    errors: list[str] = field(
        default_factory=list,
    )

    def add_error(
        self,
        message: str,
    ) -> None:

        self.errors.append(message)

    @property
    def successful(
        self,
    ) -> bool:

        return self.translated and not self.errors


# ============================================================================
# Translation Registry
# ============================================================================


class TranslationRegistry:
    """
    Registry of Financial Translators.
    """

    def __init__(self):

        self._translators: dict[
            Type,
            FinancialTranslator,
        ] = {}

    def register(
        self,
        payload_type: Type,
        translator: FinancialTranslator,
    ) -> None:

        self._translators[
            payload_type
        ] = translator

    def unregister(
        self,
        payload_type: Type,
    ) -> None:

        self._translators.pop(
            payload_type,
            None,
        )

    def translator(
        self,
        payload_type: Type,
    ) -> FinancialTranslator | None:

        return self._translators.get(
            payload_type,
        )

    def clear(
        self,
    ) -> None:

        self._translators.clear()

    def count(
        self,
    ) -> int:

        return len(
            self._translators,
        )


# ============================================================================
# Translation Service
# ============================================================================


class TranslationService:
    """
    Canonical Financial Translation Service.
    """

    def __init__(
        self,
        registry: TranslationRegistry | None = None,
    ) -> None:

        self.registry = (
            registry
            or TranslationRegistry()
        )

    def register(
        self,
        payload_type: Type,
        translator: FinancialTranslator,
    ) -> None:

        self.registry.register(
            payload_type,
            translator,
        )

    def translate(
        self,
        payload_type: Type,
        payload,
    ) -> TranslationResult:

        translator = self.registry.translator(
            payload_type,
        )

        if translator is None:

            return TranslationResult(
                translated=False,
                errors=[
                    f"No translator registered for "
                    f"{payload_type.__name__}"
                ],
            )

        evidence = translator.translate(
            payload,
        )

        return TranslationResult(

            translated=True,

            evidence=evidence,
        )


__all__ = [
    "TranslationAccessor",
    "FinancialTranslator",
    "TranslationResult",
    "TranslationRegistry",
    "TranslationService",
]