"""
Trading Truth Layer (TTL)

Gateway Engine

Canonical Validators

Institutional validation utilities for Gateway Engine evidence.

Validators are provider-independent and operate only on canonical
Gateway Engine models.
"""

from __future__ import annotations

from typing import Iterable
from typing import List
from typing import Optional

from .exceptions import InvalidEvidenceError
from .models import (
    AccountEvidence,
    AuthenticationEvidence,
    ConnectionEvidence,
    EndpointEvidence,
    ExecutionEvidence,
    GatewayEvidence,
    GatewayEvidencePackage,
    InstrumentEvidence,
    MarketDataEvidence,
    OrderEvidence,
    PositionEvidence,
    QuoteEvidence,
    SessionEvidence,
    TradeEvidence,
)


# ============================================================================
# Validation Result
# ============================================================================


class ValidationResult:
    """
    Result of validating one or more canonical evidence objects.
    """

    def __init__(self) -> None:

        self.errors: List[str] = []

        self.warnings: List[str] = []

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
    Base validator shared by every Gateway validator.
    """

    def validate(self, evidence) -> ValidationResult:

        raise NotImplementedError


# ============================================================================
# Common Validation Helpers
# ============================================================================


def require(
    result: ValidationResult,
    value,
    field_name: str,
) -> None:
    """
    Require a field to exist.
    """

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


def validate_identity(result, evidence):

    require(
        result,
        evidence.identity,
        "identity",
    )

    if evidence.identity:

        require_string(
            result,
            evidence.identity.provider_name,
            "provider_name",
        )


# ============================================================================
# Individual Validators
# ============================================================================


class GatewayValidator(BaseValidator):

    def validate(
        self,
        evidence: GatewayEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        require_string(
            result,
            evidence.gateway_name,
            "gateway_name",
        )

        return result


class SessionValidator(BaseValidator):

    def validate(
        self,
        evidence: SessionEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        return result


class AuthenticationValidator(BaseValidator):

    def validate(
        self,
        evidence: AuthenticationEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        return result


class EndpointValidator(BaseValidator):

    def validate(
        self,
        evidence: EndpointEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        return result


class ConnectionValidator(BaseValidator):

    def validate(
        self,
        evidence: ConnectionEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        return result


class AccountValidator(BaseValidator):

    def validate(
        self,
        evidence: AccountEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        return result


class InstrumentValidator(BaseValidator):

    def validate(
        self,
        evidence: InstrumentEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        require_string(
            result,
            evidence.symbol,
            "symbol",
        )

        return result


class MarketDataValidator(BaseValidator):

    def validate(
        self,
        evidence: MarketDataEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        require_string(
            result,
            evidence.symbol,
            "symbol",
        )

        return result


class QuoteValidator(BaseValidator):

    def validate(
        self,
        evidence: QuoteEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        require_string(
            result,
            evidence.symbol,
            "symbol",
        )

        return result


class OrderValidator(BaseValidator):

    def validate(
        self,
        evidence: OrderEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        require_string(
            result,
            evidence.symbol,
            "symbol",
        )

        return result


class ExecutionValidator(BaseValidator):

    def validate(
        self,
        evidence: ExecutionEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        require_string(
            result,
            evidence.symbol,
            "symbol",
        )

        return result


class PositionValidator(BaseValidator):

    def validate(
        self,
        evidence: PositionEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        require_string(
            result,
            evidence.symbol,
            "symbol",
        )

        return result


class TradeValidator(BaseValidator):

    def validate(
        self,
        evidence: TradeEvidence,
    ) -> ValidationResult:

        result = ValidationResult()

        validate_identity(result, evidence)

        require_string(
            result,
            evidence.symbol,
            "symbol",
        )

        return result


# ============================================================================
# Package Validator
# ============================================================================


class GatewayEvidencePackageValidator(BaseValidator):
    """
    Validates an entire GatewayEvidencePackage.
    """

    def validate(
        self,
        package: GatewayEvidencePackage,
    ) -> ValidationResult:

        result = ValidationResult()

        validators = {

            GatewayEvidence: GatewayValidator(),

            SessionEvidence: SessionValidator(),

            AuthenticationEvidence: AuthenticationValidator(),

            EndpointEvidence: EndpointValidator(),

            ConnectionEvidence: ConnectionValidator(),

            AccountEvidence: AccountValidator(),

            InstrumentEvidence: InstrumentValidator(),

            MarketDataEvidence: MarketDataValidator(),

            QuoteEvidence: QuoteValidator(),

            OrderEvidence: OrderValidator(),

            ExecutionEvidence: ExecutionValidator(),

            PositionEvidence: PositionValidator(),

            TradeEvidence: TradeValidator(),
        }

        def validate_object(obj):

            if obj is None:

                return

            validator = validators.get(type(obj))

            if validator is None:

                result.add_warning(
                    f"No validator registered for "
                    f"{type(obj).__name__}"
                )

                return

            object_result = validator.validate(obj)

            result.errors.extend(
                object_result.errors
            )

            result.warnings.extend(
                object_result.warnings
            )

        validate_object(package.gateway)

        validate_object(package.session)

        validate_object(package.authentication)

        validate_object(package.endpoint)

        validate_object(package.connection)

        validate_object(package.account)

        for collection in (

            package.instruments,

            package.market_data,

            package.quotes,

            package.orders,

            package.executions,

            package.positions,

            package.trades,

        ):

            for obj in collection:

                validate_object(obj)

        return result


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "ValidationResult",

    "BaseValidator",

    "GatewayValidator",

    "SessionValidator",

    "AuthenticationValidator",

    "EndpointValidator",

    "ConnectionValidator",

    "AccountValidator",

    "InstrumentValidator",

    "MarketDataValidator",

    "QuoteValidator",

    "OrderValidator",

    "ExecutionValidator",

    "PositionValidator",

    "TradeValidator",

    "GatewayEvidencePackageValidator",
]