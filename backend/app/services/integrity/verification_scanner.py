from app.models.claim_schema import ClaimSchema

from app.services.integrity.common import (
    create_alert,
    SEVERITY_WARNING,
)


def scan_verification_integrity(
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
            schema.status in [
                "published",
                "locked",
            ]
            and not schema.claim_hash
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_WARNING,
                alert_type="VERIFICATION_ROUTE_BROKEN",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} cannot be verified publicly.",
            )