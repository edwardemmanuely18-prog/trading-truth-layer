from app.models.claim_schema import ClaimSchema

from app.services.claim_service import (
    compute_claim_hash,
)

from app.services.integrity.common import (
    create_alert,
    resolve_alert,
    SEVERITY_HIGH,
)


def scan_evidence_integrity(
    db,
    workspace_id,
):
    schemas = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .all()
    )

    for schema in schemas:

        if not schema.claim_hash:

            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_HIGH,
                alert_type="CLAIM_HASH_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} has no claim hash.",
            )
        

            continue

        else:

            resolve_alert(
                db,
                "CLAIM_HASH_MISSING",
                "claim_schema",
                schema.id,
            )

        current_hash = (
            compute_claim_hash(
                schema
            )
        )

        if (
            current_hash
            != schema.claim_hash
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_HIGH,
                alert_type="CLAIM_HASH_MISMATCH",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} hash mismatch.",
            )
        else:
            resolve_alert(
                db,
                "CLAIM_HASH_MISMATCH",
                "claim_schema",
                schema.id,
            )