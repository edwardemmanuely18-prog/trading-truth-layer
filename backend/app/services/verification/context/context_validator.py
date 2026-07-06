from __future__ import annotations

from app.services.verification.verification_context import (
    VerificationContext,
)


def validate_context(
    context: VerificationContext,
) -> None:
    """
    Canonical TVS context validation.

    Ensures every verification run has
    the minimum required objects before
    scoring begins.

    This performs validation only.

    It does NOT compute any score.
    """

    if context is None:
        raise ValueError(
            "VerificationContext cannot be None."
        )

    if context.claim_schema is None:
        raise ValueError(
            "Missing ClaimSchema."
        )

    if context.workspace is None:
        raise ValueError(
            "Missing Workspace."
        )

    if context.trades is None:
        raise ValueError(
            "Trades collection is missing."
        )

    if context.evidence_records is None:
        context.evidence_records = []

    if context.audit_events is None:
        context.audit_events = []

    if context.review_statements is None:
        context.review_statements = []

    if context.disputes is None:
        context.disputes = []

    if context.integrity_alerts is None:
        context.integrity_alerts = []

    if context.broker_connections is None:
        context.broker_connections = []

    return