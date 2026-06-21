from app.models.claim_schema import ClaimSchema

from app.services.integrity.common import (
    create_alert,
    SEVERITY_HIGH,
)


def scan_public_integrity(
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
            schema.visibility == "public"
            and not schema.claim_hash
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_HIGH,
                alert_type="PUBLIC_RECORD_UNVERIFIABLE",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} public but not verifiable.",
            )

        if (
            schema.visibility == "public"
            and schema.status == "draft"
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_HIGH,
                alert_type="PUBLIC_DRAFT_EXPOSURE",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Draft claim exposed publicly.",
            )