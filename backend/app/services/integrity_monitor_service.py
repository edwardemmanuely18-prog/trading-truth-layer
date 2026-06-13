from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from app.services.claim_scope_service import (
    resolve_schema_trades,
)

from app.services.claim_forensic_service import (
    validate_claim_forensics,
)


def evaluate_claim_integrity(
    db: Session,
    schema: ClaimSchema,
):
    trades = resolve_schema_trades(
        schema,
        db,
    )

    forensic_validation = (
        validate_claim_forensics(
            db=db,
            workspace_id=schema.workspace_id,
            trades=trades,
        )
    )

    return {
        "claim_id": schema.id,
        "claim_status": schema.status,
        "fully_verified":
            forensic_validation["fully_verified"],
        "forensic_coverage":
            forensic_validation["forensic_coverage"],
        "verified_trades":
            forensic_validation["verified_trades"],
        "total_trades":
            forensic_validation["total_trades"],
        "missing_trades":
            forensic_validation["missing_trades"],
    }


def scan_workspace_claims(
    db: Session,
    workspace_id: int,
):
    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .all()
    )

    return [
        evaluate_claim_integrity(
            db=db,
            schema=claim,
        )
        for claim in claims
    ]