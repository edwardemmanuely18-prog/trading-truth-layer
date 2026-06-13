from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from app.services.claim_scope_service import (
    resolve_schema_trades,
    resolve_claim_integrity_status,
)

from app.services.claim_forensic_service import (
    validate_claim_forensics,
)

from app.services.verification_timeline_service import (
    build_claim_timeline,
)


def build_due_diligence_report(
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

    integrity_status = (
        resolve_claim_integrity_status(
            schema,
            trades,
        )
    )

    timeline = build_claim_timeline(
        db=db,
        claim_id=schema.id,
    )

    return {
        "claim_id": schema.id,
        "claim_name": schema.name,
        "workspace_id": schema.workspace_id,

        "claim_status": schema.status,

        "integrity_status": integrity_status,

        "forensics": forensic_validation,

        "timeline": timeline,

        "trade_count": len(trades),

        "claim_hash": schema.claim_hash,

        "locked_trade_set_hash":
            schema.locked_trade_set_hash,

        "verified_at":
            schema.verified_at,

        "published_at":
            schema.published_at,

        "locked_at":
            schema.locked_at,
    }