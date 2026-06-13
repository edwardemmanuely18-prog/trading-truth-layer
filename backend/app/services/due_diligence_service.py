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

    total_trades = len(trades)

    verified_trades = (
        forensic_validation["verified_trades"]
    )

    forensic_coverage = (
        forensic_validation["forensic_coverage"]
    )

    evidence_coverage = (
        forensic_coverage * 100
    )

    integrity_coverage = (
        100.0
        if integrity_status == "valid"
        else 0.0
    )

    verification_coverage = (
        100.0
        if schema.status in [
            "verified",
            "published",
            "locked",
        ]
        else 0.0
    )

    risk_flags = []

    if total_trades == 0:
        risk_flags.append(
            "empty_claim_scope"
        )

    if forensic_coverage < 1.0:
        risk_flags.append(
            "incomplete_forensic_coverage"
        )

    if integrity_status == "compromised":
        risk_flags.append(
            "integrity_compromised"
        )

    if schema.status == "draft":
        risk_flags.append(
            "claim_not_verified"
        )

    return {
        "claim_id": schema.id,
        "claim_name": schema.name,
        "workspace_id": schema.workspace_id,

        "claim_status": schema.status,

        "integrity_status": integrity_status,

        "trade_count": total_trades,

        "evidence_coverage":
            evidence_coverage,

        "integrity_coverage":
            integrity_coverage,

        "verification_coverage":
            verification_coverage,

        "risk_flags":
            risk_flags,

        "forensics":
            forensic_validation,

        "timeline":
            timeline,

        "claim_hash":
            schema.claim_hash,

        "locked_trade_set_hash":
            schema.locked_trade_set_hash,

        "verified_at":
            schema.verified_at,

        "published_at":
            schema.published_at,

        "locked_at":
            schema.locked_at,
    }