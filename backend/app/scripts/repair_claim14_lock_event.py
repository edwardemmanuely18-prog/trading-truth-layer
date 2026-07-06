from app.core.db import SessionLocal

from app.models.claim_schema import ClaimSchema
from app.models.audit_event import AuditEvent


def run():

    db = SessionLocal()

    try:

        claim = (
            db.query(ClaimSchema)
            .filter(
                ClaimSchema.id == 14
            )
            .first()
        )

        if not claim:

            print(
                "Claim 14 not found."
            )

            return

        existing = (
            db.query(AuditEvent)
            .filter(
                AuditEvent.event_type
                == "claim_schema_locked",

                AuditEvent.entity_type
                == "claim_schema",

                AuditEvent.entity_id
                == str(claim.id),
            )
            .first()
        )

        if existing:

            print(
                "Lock audit event already exists."
            )

            return

        db.add(
            AuditEvent(
                event_type="claim_schema_locked",
                entity_type="claim_schema",
                entity_id=str(claim.id),
                workspace_id=str(
                    claim.workspace_id
                ),
                actor_id=None,
                old_state=None,
                new_state=None,
                metadata_json=None,
                created_at=claim.locked_at,
            )
        )

        db.commit()

        print(
            "Inserted lock audit event "
            "for Claim 14."
        )

    finally:

        db.close()


if __name__ == "__main__":
    run()