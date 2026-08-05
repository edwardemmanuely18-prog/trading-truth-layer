"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Canonical Validation Layer
"""

from __future__ import annotations

from typing import Iterable, Optional

from .exceptions import PackageError, ValidationError
from .models import (
    DesktopEvidencePackage,
    Evidence,
)


# ============================================================================
# Primitive Helpers
# ============================================================================


def require(
    condition: bool,
    message: str,
) -> None:
    """
    Raise ValidationError when a required condition fails.
    """

    if not condition:
        raise ValidationError(message)


def require_not_none(
    value,
    name: str,
) -> None:
    """
    Ensure a required value exists.
    """

    if value is None:
        raise ValidationError(f"{name} cannot be None.")


def require_not_empty(
    value,
    name: str,
) -> None:
    """
    Ensure a string-like value is not empty.
    """

    require_not_none(value, name)

    if hasattr(value, "__len__") and len(value) == 0:
        raise ValidationError(f"{name} cannot be empty.")


# ============================================================================
# Evidence Validation
# ============================================================================


def validate_identity(evidence: Evidence) -> None:
    """
    Validate evidence identity.
    """

    require_not_none(evidence.identity, "identity")

    require_not_empty(
        evidence.identity.evidence_id,
        "identity.evidence_id",
    )

    require_not_empty(
        evidence.identity.evidence_type,
        "identity.evidence_type",
    )


def validate_metadata(evidence: Evidence) -> None:
    """
    Validate evidence metadata.
    """

    require_not_none(evidence.metadata, "metadata")


def validate_provenance(evidence: Evidence) -> None:
    """
    Validate evidence provenance.
    """

    require_not_none(
        evidence.provenance,
        "provenance",
    )


def validate_evidence(
    evidence: Evidence,
) -> None:
    """
    Validate a canonical evidence object.
    """

    require_not_none(
        evidence,
        "evidence",
    )

    validate_identity(evidence)

    validate_metadata(evidence)

    validate_provenance(evidence)


# ============================================================================
# Collection Validation
# ============================================================================


def validate_collection(
    collection: Optional[Iterable[Evidence]],
    name: str,
) -> None:
    """
    Validate an iterable of evidence objects.
    """

    if collection is None:
        return

    for item in collection:
        try:
            validate_evidence(item)
        except ValidationError as exc:
            raise ValidationError(
                f"{name}: {exc}"
            ) from exc


# ============================================================================
# Desktop Evidence Package
# ============================================================================


def validate_package(
    package: DesktopEvidencePackage,
) -> None:
    """
    Validate a DesktopEvidencePackage.
    """

    if package is None:
        raise PackageError(
            "DesktopEvidencePackage cannot be None."
        )

    singleton_evidence = (
        package.terminal,
        package.user,
        package.broker,
        package.server,
        package.account,
        package.balance,
        package.margin,
        package.equity,
        package.buying_power,
        package.history,
    )

    for evidence in singleton_evidence:
        if evidence is not None:
            validate_evidence(evidence)

    validate_collection(
        package.symbols,
        "symbols",
    )

    validate_collection(
        package.prices,
        "prices",
    )

    validate_collection(
        package.orders,
        "orders",
    )

    validate_collection(
        package.executions,
        "executions",
    )

    validate_collection(
        package.deals,
        "deals",
    )

    validate_collection(
        package.trades,
        "trades",
    )

    validate_collection(
        package.positions,
        "positions",
    )

    validate_collection(
        package.activities,
        "activities",
    )


# ============================================================================
# Convenience Helpers
# ============================================================================


def is_valid_evidence(
    evidence: Evidence,
) -> bool:
    """
    Return True if an evidence object is valid.
    """

    try:
        validate_evidence(evidence)
        return True
    except ValidationError:
        return False


def is_valid_package(
    package: DesktopEvidencePackage,
) -> bool:
    """
    Return True if a package is valid.
    """

    try:
        validate_package(package)
        return True
    except (ValidationError, PackageError):
        return False


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "require",
    "require_not_none",
    "require_not_empty",
    "validate_identity",
    "validate_metadata",
    "validate_provenance",
    "validate_evidence",
    "validate_collection",
    "validate_package",
    "is_valid_evidence",
    "is_valid_package",
]