from __future__ import annotations

from app.services.verification.verification_models import (
    ComponentResult,
)

from app.services.verification.scoring_weights import (
    TRANSPARENCY,
)

from app.services.verification.verification_context import (
    VerificationContext,
)


def compute_transparency_score(
    context: VerificationContext,
) -> ComponentResult:

    claim = context.claim_schema

    score = 0.0

    public = bool(
        getattr(
            claim,
            "is_public",
            False,
        )
    )

    verification = bool(
        getattr(
            claim,
            "verification_hash",
            None,
        )
    )

    pdf = bool(
        getattr(
            claim,
            "locked_pdf_path",
            None,
        )
    )

    claim_hash = bool(
        getattr(
            claim,
            "claim_hash",
            None,
        )
    )

    evidence_snapshot = bool(
        getattr(
            claim,
            "evidence_snapshot_hash",
            None,
        )
    )

    scope_hash = bool(
        getattr(
            claim,
            "scope_hash",
            None,
        )
    )

    lifecycle_hash = bool(
        getattr(
            claim,
            "lifecycle_hash",
            None,
        )
    )

    integrity_snapshot = bool(
        getattr(
            claim,
            "integrity_snapshot_json",
            None,
        )
    )

    if public:
        score += 1

    if verification:
        score += 1

    if claim_hash:
        score += 1

    if pdf:
        score += 1

    if evidence_snapshot:
        score += 1

    if scope_hash:
        score += 1

    if lifecycle_hash:
        score += 1

    if integrity_snapshot:
        score += 1

    return ComponentResult(

        name="Transparency",

        earned_points=min(
            score,
            TRANSPARENCY,
        ),

        maximum_points=TRANSPARENCY,

        status="Transparent",

        reason=(
            "Derived from public "
            "verification assets."
        ),

        details={

            "public": public,

            "verification": verification,

            "claim_hash": claim_hash,

            "pdf": pdf,

            "evidence_snapshot": evidence_snapshot,

            "scope_hash": scope_hash,

            "lifecycle_hash": lifecycle_hash,

            "integrity_snapshot": integrity_snapshot,

        },

    )