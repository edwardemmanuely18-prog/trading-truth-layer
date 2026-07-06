from app.core.db import SessionLocal

from app.models.integrity_alert import IntegrityAlert
from app.models.claim_schema import ClaimSchema
from app.models.audit_event import AuditEvent

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
    compute_integrity_snapshot,
)

import json


def run():

    db = SessionLocal()

    try:

        resolved = 0

        alerts = (
            db.query(IntegrityAlert)
            .filter(
                IntegrityAlert.status == "open"
            )
            .all()
        )

        for alert in alerts:

            #
            # VERIFY_AUDIT_MISSING
            #

            if (
                alert.alert_type
                == "VERIFY_AUDIT_MISSING"
            ):

                events = (
                    db.query(AuditEvent)
                    .filter(
                        AuditEvent.entity_type
                        == "claim_schema",

                        AuditEvent.entity_id
                        == alert.entity_id,
                    )
                    .all()
                )

                has_verify = any(
                    (
                        "verify"
                        in str(
                            e.event_type
                        ).lower()
                        or
                        "verified"
                        in str(
                            e.event_type
                        ).lower()
                    )
                    for e in events
                )

                if has_verify:

                    alert.status = "resolved"
                    resolved += 1

                continue

            #
            # AUDIT_ACTOR_MISSING
            #

            if (
                alert.alert_type
                == "AUDIT_ACTOR_MISSING"
            ):

                event = (
                    db.query(AuditEvent)
                    .filter(
                        AuditEvent.id
                        == int(alert.entity_id)
                    )
                    .first()
                )

                if not event:

                    alert.status = "resolved"
                    resolved += 1
                    continue

                requires_actor = (
                    event.event_type
                    in [
                        "login_success",
                        "login_failed",
                        "workspace_membership_role_updated",
                    ]
                )

                if not requires_actor:

                    alert.status = "resolved"
                    resolved += 1

                continue

            #
            # LIFECYCLE_HASH_MISMATCH
            #

            if (
                alert.alert_type
                == "LIFECYCLE_HASH_MISMATCH"
            ):

                claim = (
                    db.query(ClaimSchema)
                    .filter(
                        ClaimSchema.id
                        == int(alert.entity_id)
                    )
                    .first()
                )

                if not claim:
                    alert.status = "resolved"
                    resolved += 1
                    continue

                try:

                    stored = json.loads(
                        claim.integrity_snapshot_json
                        or "{}"
                    )

                    trades = (
                        resolve_schema_trades(
                            claim,
                            db,
                        )
                    )

                    current = (
                        compute_integrity_snapshot(
                            claim,
                            trades,
                        )
                    )

                    if (
                        stored.get(
                            "lifecycle_hash"
                        )
                        ==
                        current.get(
                            "lifecycle_hash"
                        )
                    ):
                        alert.status = "resolved"
                        resolved += 1

                except Exception:

                    pass

        db.commit()

        print(
            f"Resolved {resolved} stale alerts."
        )

    finally:

        db.close()


if __name__ == "__main__":
    run()