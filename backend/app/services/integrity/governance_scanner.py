from app.models.claim_schema import ClaimSchema

from app.services.integrity.common import (
    create_alert,
    SEVERITY_CRITICAL,
)


def scan_governance_integrity(
    db,
    workspace_id,
):
    schemas = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    for schema in schemas:

        if (
            schema.status == "locked"
            and not schema.claim_hash
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_CRITICAL,
                alert_type="CANONICAL_HASH_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} missing canonical hash.",
            )

        if (
            schema.status == "locked"
            and not schema.locked_trade_set_hash
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_CRITICAL,
                alert_type="LOCK_HASH_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} missing locked trade hash.",
            )

        if (
            schema.status == "locked"
            and (
                not schema.integrity_snapshot_json
                or schema.integrity_snapshot_json
                == "{}"
            )
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_CRITICAL,
                alert_type="INTEGRITY_SNAPSHOT_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} missing integrity snapshot.",
            )