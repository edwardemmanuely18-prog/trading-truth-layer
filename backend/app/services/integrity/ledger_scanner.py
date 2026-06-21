import json

from app.models.claim_schema import ClaimSchema

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
    compute_integrity_snapshot,
)

from app.services.integrity.common import (
    create_alert,
    SEVERITY_FATAL,
    SEVERITY_CRITICAL,
)


def scan_ledger_integrity(
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
            stored_snapshot.get("trade_hash")
            and
            stored_snapshot["trade_hash"]
            != current_snapshot["trade_hash"]
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_FATAL,
                alert_type="TRADE_HASH_MISMATCH",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} trade integrity changed.",
            )

        stored_trade_count = (
            stored_snapshot.get(
                "trade_count"
            )
        )

        current_trade_count = (
            len(trades)
        )

        if (
            stored_trade_count is not None
            and stored_trade_count
            != current_trade_count
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_CRITICAL,
                alert_type="TRADE_COUNT_MISMATCH",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} trade count changed.",
            )