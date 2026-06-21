import json

from app.models.claim_schema import ClaimSchema

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
    compute_integrity_snapshot,
)

from app.services.integrity.common import (
    create_alert,
    SEVERITY_WARNING,
)


def scan_lifecycle_integrity(
    db,
    workspace_id,
):
    schemas = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status == "locked",
        )
        .all()
    )

    for schema in schemas:

        trades = resolve_schema_trades(
            schema,
            db,
        )

        current_snapshot = (
            compute_integrity_snapshot(
                schema,
                trades,
            )
        )

        try:
            stored_snapshot = json.loads(
                schema.integrity_snapshot_json
                or "{}"
            )
        except Exception:
            stored_snapshot = {}

        if (
            stored_snapshot.get(
                "lifecycle_hash"
            )
            and
            stored_snapshot["lifecycle_hash"]
            != current_snapshot["lifecycle_hash"]
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_WARNING,
                alert_type="LIFECYCLE_HASH_MISMATCH",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} lifecycle changed.",
            )

        if (
            schema.status == "locked"
            and schema.locked_at is None
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_WARNING,
                alert_type="LOCK_STATE_INCONSISTENT",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} lock state inconsistent.",
            )