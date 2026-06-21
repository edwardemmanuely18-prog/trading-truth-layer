from app.models.claim_schema import ClaimSchema
from app.models.audit_event import AuditEvent

from app.services.integrity.common import (
    create_alert,
    SEVERITY_WARNING,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL,
)


def scan_audit_integrity(
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

        events = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type
                == "claim_schema",

                AuditEvent.entity_id
                == str(schema.id),
            )
            .order_by(
                AuditEvent.created_at.asc()
            )
            .all()
        )

        # ====================================
        # NO AUDIT TRAIL
        # ====================================

        if len(events) == 0:

            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_CRITICAL,
                alert_type="AUDIT_TRAIL_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} has no audit trail.",
            )

            continue

        # ====================================
        # VERIFY EVENT
        # ====================================

        if (
            schema.status in [
                "verified",
                "published",
                "locked",
            ]
            and not any(
                "verify"
                in str(
                    e.event_type
                ).lower()
                for e in events
            )
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_HIGH,
                alert_type="VERIFY_AUDIT_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} missing verify audit event.",
            )

        # ====================================
        # PUBLISH EVENT
        # ====================================

        if (
            schema.status in [
                "published",
                "locked",
            ]
            and not any(
                "publish"
                in str(
                    e.event_type
                ).lower()
                for e in events
            )
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_HIGH,
                alert_type="PUBLISH_AUDIT_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} missing publish audit event.",
            )

        # ====================================
        # LOCK EVENT
        # ====================================

        if (
            schema.status == "locked"
            and not any(
                "lock"
                in str(
                    e.event_type
                ).lower()
                for e in events
            )
        ):
            create_alert(
                db=db,
                workspace_id=workspace_id,
                severity=SEVERITY_HIGH,
                alert_type="LOCK_AUDIT_MISSING",
                entity_type="claim_schema",
                entity_id=schema.id,
                message=f"Claim {schema.id} missing lock audit event.",
            )

        # ====================================
        # ACTOR CHECK
        # ====================================

        for event in events:

            if not event.actor_id:

                create_alert(
                    db=db,
                    workspace_id=workspace_id,
                    severity=SEVERITY_WARNING,
                    alert_type="AUDIT_ACTOR_MISSING",
                    entity_type="audit_event",
                    entity_id=event.id,
                    message=f"Audit event {event.id} missing actor.",
                )

            if not event.created_at:

                create_alert(
                    db=db,
                    workspace_id=workspace_id,
                    severity=SEVERITY_HIGH,
                    alert_type="AUDIT_TIMESTAMP_INVALID",
                    entity_type="audit_event",
                    entity_id=event.id,
                    message=f"Audit event {event.id} missing timestamp.",
                )

            if (
                not event.old_state
                and not event.new_state
            ):
                create_alert(
                    db=db,
                    workspace_id=workspace_id,
                    severity=SEVERITY_WARNING,
                    alert_type="AUDIT_STATE_MISSING",
                    entity_type="audit_event",
                    entity_id=event.id,
                    message=f"Audit event {event.id} missing state.",
                )