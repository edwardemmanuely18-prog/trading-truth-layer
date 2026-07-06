from app.models.claim_schema import ClaimSchema

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
)

from app.services.trade_metrics_service import (
    compute_trade_metrics,
)

from app.services.integrity.common import (
    create_alert,
    resolve_alert,
    SEVERITY_WARNING,
)


def scan_metrics_integrity(
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

        trades = (
            resolve_schema_trades(
                schema,
                db,
            )
        )

        metrics = (
            compute_trade_metrics(
                trades
            )
        )

        if (
            metrics["trade_count"] == 0
            and schema.status in [
                "verified",
                "published",
                "locked",
            ]
        ):

            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_WARNING,
                alert_type="EMPTY_VERIFIED_CLAIM",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} verified with zero trades.",
            )

        else:

            resolve_alert(
                db,
                "EMPTY_VERIFIED_CLAIM",
                "claim_schema",
                schema.id,
            )

        if metrics["profit_factor"] < 0:

            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_WARNING,
                alert_type="INVALID_PROFIT_FACTOR",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} contains invalid metrics.",
            )

        else:

            resolve_alert(
                db,
                "INVALID_PROFIT_FACTOR",
                "claim_schema",
                schema.id,
            )