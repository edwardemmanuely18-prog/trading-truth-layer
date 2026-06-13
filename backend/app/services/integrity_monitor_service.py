from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from app.services.claim_scope_service import (
    resolve_schema_trades,
)

from app.services.claim_forensic_service import (
    validate_claim_forensics,
)

from app.services.audit_service import (
    log_audit_event,
)

from app.services.integrity_alert_service import (
    create_integrity_alert,
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


def enforce_claim_integrity(
    db: Session,
    schema: ClaimSchema,
):
    integrity = evaluate_claim_integrity(
        db=db,
        schema=schema,
    )

    if schema.status != "locked":
        return integrity

    if integrity["fully_verified"]:
        return integrity

    previous_status = schema.status

    schema.status = "compromised"

    from app.models.integrity_alert import (
        IntegrityAlert,
    )

    existing_alert = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id
            == schema.workspace_id,
            IntegrityAlert.claim_id
            == schema.id,
            IntegrityAlert.alert_type
            == "claim_compromised",
            IntegrityAlert.status
            == "open",
        )
        .first()
    )

    if existing_alert is None:

        create_integrity_alert(
            db=db,
            workspace_id=schema.workspace_id,
            claim_id=schema.id,
            alert_type="claim_compromised",
            severity="critical",
            summary=(
                f"Claim {schema.id} failed "
                f"forensic verification."
            ),
        )

    create_integrity_alert(
        db=db,
        workspace_id=schema.workspace_id,
        claim_id=schema.id,
        alert_type="claim_compromised",
        severity="critical",
        summary=(
            f"Claim {schema.id} failed "
            f"forensic verification."
        ),
    )

    log_audit_event(
        db,
        event_type="claim_compromised",
        entity_type="claim_schema",
        entity_id=schema.id,
        workspace_id=schema.workspace_id,
        old_state={
            "status": previous_status,
        },
        new_state={
            "status": schema.status,
        },
        metadata={
            "forensic_coverage":
                integrity["forensic_coverage"],
            "verified_trades":
                integrity["verified_trades"],
            "total_trades":
                integrity["total_trades"],
        },
    )

    db.commit()
    db.refresh(schema)

    return integrity


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

    results = []

    for claim in claims:

        result = enforce_claim_integrity(
            db=db,
            schema=claim,
        )

        results.append(result)

    return results