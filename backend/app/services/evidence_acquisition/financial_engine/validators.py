"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Canonical Validators

Institutional validation utilities for Financial Engine evidence.

Validators are provider-independent and operate only on canonical
Financial Engine models.
"""

from __future__ import annotations

from typing import Dict
from typing import Optional
from typing import Type

from .exceptions import InvalidEvidenceError
from .models import (
    BankGuaranteeEvidence,
    BankStatementEvidence,
    CanonicalFinancialEvidence,
    CashBalanceEvidence,
    CashTransferEvidence,
    CollateralEvidence,
    CorporateActionEvidence,
    Counterparty,
    Currency,
    FinancialAccount,
    FinancialEvidence,
    FinancialInstitution,
    FundingEventEvidence,
    LetterOfCreditEvidence,
    MarginEvidence,
    PaymentEvidence,
    SettlementConfirmationEvidence,
    SettlementInstructionEvidence,
    CustodyHoldingEvidence,
)


# ============================================================================
# Validation Result
# ============================================================================


class ValidationResult:
    """
    Result of validating one or more canonical evidence objects.
    """

    def __init__(self) -> None:

        self.errors: list[str] = []

        self.warnings: list[str] = []

    @property
    def valid(self) -> bool:

        return len(self.errors) == 0

    def add_error(self, message: str) -> None:

        self.errors.append(message)

    def add_warning(self, message: str) -> None:

        self.warnings.append(message)

    def raise_if_invalid(self) -> None:

        if self.errors:

            raise InvalidEvidenceError(
                "\n".join(self.errors)
            )


# ============================================================================
# Base Validator
# ============================================================================


class BaseValidator:
    """
    Base validator shared by every Financial validator.
    """

    def validate(
        self,
        evidence,
    ) -> ValidationResult:

        raise NotImplementedError


# ============================================================================
# Common Validation Helpers
# ============================================================================


def require(
    result: ValidationResult,
    value,
    field_name: str,
) -> None:

    if value is None:

        result.add_error(
            f"Missing required field: {field_name}"
        )


def require_string(
    result: ValidationResult,
    value: Optional[str],
    field_name: str,
) -> None:

    if not value:

        result.add_error(
            f"Missing required field: {field_name}"
        )


def validate_currency(
    result: ValidationResult,
    currency: Optional[Currency],
) -> None:

    require(result, currency, "currency")

    if currency:

        require_string(
            result,
            currency.code,
            "currency.code",
        )


def validate_institution(
    result: ValidationResult,
    institution: Optional[
        FinancialInstitution
    ],
) -> None:

    require(
        result,
        institution,
        "institution",
    )

    if institution:

        require_string(
            result,
            institution.institution_id,
            "institution_id",
        )

        require_string(
            result,
            institution.legal_name,
            "legal_name",
        )


def validate_counterparty(
    result: ValidationResult,
    counterparty: Optional[
        Counterparty
    ],
    field_name: str,
) -> None:

    require(
        result,
        counterparty,
        field_name,
    )

    if counterparty:

        require_string(
            result,
            counterparty.counterparty_id,
            f"{field_name}.counterparty_id",
        )

        require_string(
            result,
            counterparty.legal_name,
            f"{field_name}.legal_name",
        )


def validate_account(
    result: ValidationResult,
    account: Optional[
        FinancialAccount
    ],
) -> None:

    require(
        result,
        account,
        "account",
    )

    if account:

        require_string(
            result,
            account.account_id,
            "account_id",
        )

        require_string(
            result,
            account.account_number,
            "account_number",
        )

        validate_currency(
            result,
            account.currency,
        )

        validate_institution(
            result,
            account.institution,
        )


def validate_base(
    result: ValidationResult,
    evidence: FinancialEvidence,
) -> None:

    require(
        result,
        evidence.provider,
        "provider",
    )

    require(
        result,
        evidence.evidence_type,
        "evidence_type",
    )

    require(
        result,
        evidence.acquired_at,
        "acquired_at",
    )

    if evidence.account:

        validate_account(
            result,
            evidence.account,
        )


# ============================================================================
# Individual Validators
# ============================================================================


class FinancialEvidenceValidator(
    BaseValidator
):

    def validate(
        self,
        evidence: FinancialEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_base(
            result,
            evidence,
        )

        return result


class CashBalanceValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: CashBalanceEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        validate_currency(
            result,
            evidence.currency,
        )

        if evidence.available_balance < 0:

            result.add_warning(
                "available_balance is negative."
            )

        if evidence.ledger_balance < 0:

            result.add_warning(
                "ledger_balance is negative."
            )

        if evidence.booked_balance < 0:

            result.add_warning(
                "booked_balance is negative."
            )

        if evidence.pending_balance < 0:

            result.add_warning(
                "pending_balance is negative."
            )

        return result


class CashTransferValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: CashTransferEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.transfer_reference,
            "transfer_reference",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        validate_counterparty(
            result,
            evidence.sender,
            "sender",
        )

        validate_counterparty(
            result,
            evidence.receiver,
            "receiver",
        )

        if evidence.amount <= 0:

            result.add_error(
                "Transfer amount must be greater than zero."
            )

        if (
            evidence.completed_at
            and evidence.initiated_at
            and evidence.completed_at
            < evidence.initiated_at
        ):

            result.add_error(
                "completed_at cannot be earlier than initiated_at."
            )

        return result


class SettlementInstructionValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: SettlementInstructionEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.instruction_id,
            "instruction_id",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        validate_counterparty(
            result,
            evidence.delivering_party,
            "delivering_party",
        )

        validate_counterparty(
            result,
            evidence.receiving_party,
            "receiving_party",
        )

        if evidence.settlement_amount <= 0:

            result.add_error(
                "Settlement amount must be greater than zero."
            )

        if evidence.settlement_date is None:

            result.add_warning(
                "settlement_date is missing."
            )

        return result


class SettlementConfirmationValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: SettlementConfirmationEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.confirmation_id,
            "confirmation_id",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        if evidence.settled_amount <= 0:

            result.add_error(
                "Settled amount must be greater than zero."
            )

        if evidence.settled_at is None:

            result.add_warning(
                "settled_at is missing."
            )

        if (
            evidence.instruction_reference is None
            or evidence.instruction_reference == ""
        ):

            result.add_warning(
                "instruction_reference is missing."
            )

        return result


class CustodyHoldingValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: CustodyHoldingEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.security_id,
            "security_id",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        if evidence.quantity < 0:

            result.add_error(
                "Quantity cannot be negative."
            )

        if evidence.market_value < 0:

            result.add_error(
                "Market value cannot be negative."
            )

        if evidence.valuation_date is None:

            result.add_warning(
                "valuation_date is missing."
            )

        return result


class FundingEventValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: FundingEventEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.funding_reference,
            "funding_reference",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        validate_counterparty(
            result,
            evidence.counterparty,
            "counterparty",
        )

        if evidence.amount <= 0:

            result.add_error(
                "Funding amount must be greater than zero."
            )

        if evidence.event_time is None:

            result.add_warning(
                "event_time is missing."
            )

        if (
            evidence.maturity_date
            and evidence.event_time
            and evidence.maturity_date
            < evidence.event_time
        ):

            result.add_error(
                "maturity_date cannot be earlier than event_time."
            )

        return result


class CorporateActionValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: CorporateActionEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.corporate_action_id,
            "corporate_action_id",
        )

        if (
            evidence.action_type is None
            or evidence.action_type == ""
        ):

            result.add_warning(
                "action_type is missing."
            )

        validate_currency(
            result,
            evidence.currency,
        )

        if (
            evidence.effective_date
            and evidence.announcement_date
            and evidence.effective_date
            < evidence.announcement_date
        ):

            result.add_error(
                "effective_date cannot be earlier than announcement_date."
            )

        if (
            evidence.payable_date
            and evidence.effective_date
            and evidence.payable_date
            < evidence.effective_date
        ):

            result.add_error(
                "payable_date cannot be earlier than effective_date."
            )

        return result


class BankStatementValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: BankStatementEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.statement_reference,
            "statement_reference",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        if evidence.closing_balance < 0:

            result.add_warning(
                "Closing balance is negative."
            )

        if evidence.opening_balance < 0:

            result.add_warning(
                "Opening balance is negative."
            )

        if (
            evidence.period_start
            and evidence.period_end
            and evidence.period_end
            < evidence.period_start
        ):

            result.add_error(
                "period_end cannot be earlier than period_start."
            )

        return result


class LetterOfCreditValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: LetterOfCreditEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.lc_reference,
            "lc_reference",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        validate_financial_institution(
            result,
            evidence.issuing_bank,
            "issuing_bank",
        )

        if evidence.amount <= 0:

            result.add_error(
                "Letter of Credit amount must be greater than zero."
            )

        if (
            evidence.issue_date
            and evidence.expiry_date
            and evidence.expiry_date
            < evidence.issue_date
        ):

            result.add_error(
                "expiry_date cannot be earlier than issue_date."
            )

        return result


class BankGuaranteeValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: BankGuaranteeEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.guarantee_reference,
            "guarantee_reference",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        validate_financial_institution(
            result,
            evidence.guarantor,
            "guarantor",
        )

        validate_counterparty(
            result,
            evidence.beneficiary,
            "beneficiary",
        )

        if evidence.guarantee_amount <= 0:

            result.add_error(
                "Guarantee amount must be greater than zero."
            )

        if (
            evidence.issue_date
            and evidence.expiry_date
            and evidence.expiry_date
            < evidence.issue_date
        ):

            result.add_error(
                "expiry_date cannot be earlier than issue_date."
            )

        return result


class CollateralValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: CollateralEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.collateral_id,
            "collateral_id",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        validate_counterparty(
            result,
            evidence.counterparty,
            "counterparty",
        )

        if evidence.quantity < 0:

            result.add_error(
                "Collateral quantity cannot be negative."
            )

        if evidence.market_value < 0:

            result.add_error(
                "Collateral market_value cannot be negative."
            )

        if (
            evidence.haircut is not None
            and evidence.haircut < 0
        ):

            result.add_error(
                "Haircut cannot be negative."
            )

        if evidence.valuation_date is None:

            result.add_warning(
                "valuation_date is missing."
            )

        return result


class MarginValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: MarginEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.margin_id,
            "margin_id",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        if evidence.required_margin < 0:

            result.add_error(
                "required_margin cannot be negative."
            )

        if evidence.posted_margin < 0:

            result.add_error(
                "posted_margin cannot be negative."
            )

        if evidence.excess_margin < 0:

            result.add_warning(
                "excess_margin is negative."
            )

        if evidence.valuation_date is None:

            result.add_warning(
                "valuation_date is missing."
            )

        return result


class PaymentValidator(
    FinancialEvidenceValidator
):

    def validate(
        self,
        evidence: PaymentEvidence,
    ) -> ValidationResult:

        result = super().validate(
            evidence,
        )

        require_string(
            result,
            evidence.payment_reference,
            "payment_reference",
        )

        validate_currency(
            result,
            evidence.currency,
        )

        validate_counterparty(
            result,
            evidence.payer,
            "payer",
        )

        validate_counterparty(
            result,
            evidence.beneficiary,
            "beneficiary",
        )

        if evidence.amount <= 0:

            result.add_error(
                "Payment amount must be greater than zero."
            )

        if evidence.execution_date is None:

            result.add_warning(
                "execution_date is missing."
            )

        return result


# ============================================================================
# Envelope Validator
# ============================================================================


class CanonicalFinancialEvidenceValidator(
    BaseValidator
):

    def validate(
        self,
        envelope: CanonicalFinancialEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        require(
            result,
            envelope.evidence,
            "evidence",
        )

        require(
            result,
            envelope.registry,
            "registry",
        )

        require(
            result,
            envelope.provenance,
            "provenance",
        )

        require(
            result,
            envelope.publication,
            "publication",
        )

        return result


# ============================================================================
# Validator Registry
# ============================================================================


class ValidatorRegistry:

    def __init__(self) -> None:

        self._validators: Dict[
            Type[FinancialEvidence],
            BaseValidator,
        ] = {}

    def register(
        self,
        evidence_type,
        validator,
    ) -> None:

        self._validators[
            evidence_type
        ] = validator

    def validator(
        self,
        evidence_type,
    ):

        return self._validators.get(
            evidence_type
        )


# ============================================================================
# Validation Service
# ============================================================================


class ValidationService:

    def __init__(
        self,
        registry: Optional[
            ValidatorRegistry
        ] = None,
    ) -> None:

        self.registry = (
            registry
            or ValidatorRegistry()
        )

    def validate(
        self,
        evidence,
    ) -> ValidationResult:

        validator = (
            self.registry.validator(
                type(evidence)
            )
        )

        if validator is None:

            validator = (
                FinancialEvidenceValidator()
            )

        return validator.validate(
            evidence
        )


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [
    "ValidationResult",
    "BaseValidator",
    "FinancialEvidenceValidator",
    "CashBalanceValidator",
    "CashTransferValidator",
    "SettlementInstructionValidator",
    "SettlementConfirmationValidator",
    "CustodyHoldingValidator",
    "FundingEventValidator",
    "CorporateActionValidator",
    "BankStatementValidator",
    "LetterOfCreditValidator",
    "BankGuaranteeValidator",
    "CollateralValidator",
    "MarginValidator",
    "PaymentValidator",
    "CanonicalFinancialEvidenceValidator",
    "ValidatorRegistry",
    "ValidationService",
]