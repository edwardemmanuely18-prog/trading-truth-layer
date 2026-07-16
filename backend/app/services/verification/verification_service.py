from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from app.services.verification.context.context_builder import (
    build_verification_context,
)

from app.services.verification.verification_engine import (
    compute_verification_certificate,
)

from app.services.verification.claim_metrics import (
    build_claim_verification_metrics,
)

from app.services.verification.workspace_metrics import (
    build_workspace_verification_metrics,
)

from dataclasses import dataclass


# ============================================================
# CONTEXT OBJECTS
# ============================================================

@dataclass(frozen=True)
class ClaimVerificationContext:
    """
    Canonical TVS context for a single claim.

    Every single-claim consumer inside TTL
    should consume this object instead of
    assembling TVS objects independently.
    """

    certificate: object

    metrics: object


@dataclass(frozen=True)
class WorkspaceVerificationContext:
    """
    Canonical TVS context for an entire workspace.
    """

    claims: list

    certificates: list

    metrics: object


# ============================================================
# CLAIM CERTIFICATE
# ============================================================

def get_claim_verification_certificate(
    db: Session,
    claim: ClaimSchema,
):
    """
    Canonical TVS verification entry point.

    Produces the immutable VerificationCertificate
    for a single claim.
    """

    context = build_verification_context(
        db=db,
        claim_schema=claim,
    )

    return compute_verification_certificate(
        context
    )


# ============================================================
# CLAIM METRICS
# ============================================================

def get_claim_verification_metrics(
    db: Session,
    claim: ClaimSchema,
):
    """
    Canonical single-claim metrics.

    Every single-claim consumer should call
    this function instead of consuming the
    certificate directly.
    """

    certificate = (
        get_claim_verification_certificate(
            db=db,
            claim=claim,
        )
    )

    return build_claim_verification_metrics(
        certificate
    )


# ============================================================
# CLAIM CONTEXT
# ============================================================

def get_claim_verification_context(
    db: Session,
    claim: ClaimSchema,
) -> ClaimVerificationContext:
    """
    Canonical TVS context.

    Returns both the immutable
    VerificationCertificate and the
    projected ClaimVerificationMetrics.

    Every claim-level consumer should
    use this entry point.
    """

    certificate = get_claim_verification_certificate(
        db=db,
        claim=claim,
    )

    metrics = build_claim_verification_metrics(
        certificate,
    )

    return ClaimVerificationContext(
        certificate=certificate,
        metrics=metrics,
    )


def get_workspace_claims(
    db: Session,
    workspace_id: int,
):
    return (

        db.query(ClaimSchema)

        .filter(
            ClaimSchema.workspace_id == workspace_id
        )

        .all()

    )


# ============================================================
# WORKSPACE CERTIFICATES
# ============================================================

def get_workspace_claim_verification_certificates(
    db: Session,
    workspace_id: int,
    *,
    include_draft: bool = False,
):
    """
    Returns every VerificationCertificate
    belonging to the workspace.
    """

    query = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
    )

    if not include_draft:

        query = query.filter(
            ClaimSchema.status.in_(
                [
                    "verified",
                    "published",
                    "locked",
                ]
            )
        )

    claims = query.all()

    certificates = []

    for claim in claims:

        try:

            certificates.append(

                get_claim_verification_certificate(
                    db=db,
                    claim=claim,
                )

            )

        except Exception:
            #
            # One invalid claim should never
            # invalidate workspace reporting.
            #
            continue

    return certificates


# ============================================================
# WORKSPACE METRICS
# ============================================================

def get_workspace_verification_metrics(
    db: Session,
    workspace_id: int,
    *,
    include_draft: bool = False,
):
    """
    Canonical workspace verification metrics.

    Aggregates all claim certificates into a
    WorkspaceVerificationMetrics object.

    No verification calculations occur here.

    The aggregation is derived entirely from
    canonical TVS certificates.
    """

    certificates = (
        get_workspace_claim_verification_certificates(
            db=db,
            workspace_id=workspace_id,
            include_draft=include_draft,
        )
    )

    claims = (

        db.query(ClaimSchema)

        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )

        .all()

    )

    return build_workspace_verification_metrics(

        certificates,

        claims,

    )


# ============================================================
# WORKSPACE CONTEXT
# ============================================================

def get_workspace_verification_context(
    db: Session,
    workspace_id: int,
    *,
    include_draft: bool = False,
) -> WorkspaceVerificationContext:
    """
    Canonical workspace verification context.

    Used by allocator reports,
    dashboards and future institutional
    reporting modules.
    """

    claims = get_workspace_claims(

        db=db,
        workspace_id=workspace_id,

    )

    certificates = (
        get_workspace_claim_verification_certificates(
            db=db,
            workspace_id=workspace_id,
            include_draft=include_draft,
        )
    )

    claims = (

        db.query(ClaimSchema)

        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )

        .all()

    )

    metrics = build_workspace_verification_metrics(

        certificates,

        claims,

    )

    return WorkspaceVerificationContext(

        certificates=certificates,

        claims=claims,

        metrics=metrics,

    )