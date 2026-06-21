import json

from app.models.claim_schema import ClaimSchema

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
    compute_integrity_snapshot,
)

from app.services.integrity.common import (
    create_alert,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL,
    SEVERITY_FATAL,
)


def scan_evidence_authenticity_integrity(
    db,
    workspace_id,
):
    """
    Institutional-grade evidence authenticity scanner.

    Purpose:
    Detect evidence tampering,
    missing evidence lineage,
    post-lock modifications,
    and evidence integrity failures.
    """

    schemas = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    for schema in schemas:

        # ==========================================
        # EVIDENCE HASH MISSING
        # ==========================================

        if (
            schema.status == "locked"
            and not schema.evidence_snapshot_hash
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_FATAL,
                alert_type="EVIDENCE_HASH_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=(
                    f"Locked claim {schema.id} "
                    f"has no evidence snapshot hash."
                ),
            )

        # ==========================================
        # SNAPSHOT MISSING
        # ==========================================

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
                severity=SEVERITY_FATAL,
                alert_type="EVIDENCE_SNAPSHOT_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=(
                    f"Locked claim {schema.id} "
                    f"missing integrity snapshot."
                ),
            )

            continue

        # ==========================================
        # LOAD SNAPSHOT
        # ==========================================

        try:
            stored_snapshot = json.loads(
                schema.integrity_snapshot_json
                or "{}"
            )
        except Exception:

            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_FATAL,
                alert_type="SNAPSHOT_CORRUPTED",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=(
                    f"Claim {schema.id} "
                    f"integrity snapshot corrupted."
                ),
            )

            continue

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

        # ==========================================
        # EVIDENCE HASH CHANGED
        # ==========================================

        stored_evidence_hash = (
            stored_snapshot.get(
                "evidence_snapshot_hash"
            )
        )

        current_evidence_hash = (
            current_snapshot.get(
                "evidence_snapshot_hash"
            )
        )

        if (
            stored_evidence_hash
            and current_evidence_hash
            and stored_evidence_hash
            != current_evidence_hash
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_FATAL,
                alert_type="LOCKED_EVIDENCE_CHANGED",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=(
                    f"Evidence changed after lock "
                    f"for claim {schema.id}."
                ),
            )

        # ==========================================
        # TRADE SET CHANGED
        # ==========================================

        stored_trade_hash = (
            stored_snapshot.get(
                "trade_hash"
            )
        )

        current_trade_hash = (
            current_snapshot.get(
                "trade_hash"
            )
        )

        if (
            stored_trade_hash
            and current_trade_hash
            and stored_trade_hash
            != current_trade_hash
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_FATAL,
                alert_type="EVIDENCE_LINEAGE_BROKEN",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=(
                    f"Evidence lineage broken "
                    f"for claim {schema.id}."
                ),
            )

        # ==========================================
        # LOCK HASH MISSING
        # ==========================================

        if (
            schema.status == "locked"
            and not schema.locked_trade_set_hash
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_CRITICAL,
                alert_type="LOCK_REFERENCE_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=(
                    f"Locked claim {schema.id} "
                    f"missing lock reference hash."
                ),
            )

        # ==========================================
        # EVIDENCE COVERAGE FAILURE
        # ==========================================

        if (
            schema.status == "published"
            and not schema.evidence_snapshot_hash
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_HIGH,
                alert_type="EVIDENCE_COVERAGE_FAILURE",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=(
                    f"Published claim {schema.id} "
                    f"missing evidence coverage."
                ),
            )