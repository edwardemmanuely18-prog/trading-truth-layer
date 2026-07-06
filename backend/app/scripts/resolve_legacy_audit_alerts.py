from app.core.db import SessionLocal

from app.models.audit_event import AuditEvent
from app.models.integrity_alert import IntegrityAlert


def run():

    db = SessionLocal()

    try:

        alerts = (
            db.query(IntegrityAlert)
            .filter(
                IntegrityAlert.alert_type
                == "AUDIT_ACTOR_MISSING",

                IntegrityAlert.status
                == "open",
            )
            .all()
        )

        resolved = 0

        for alert in alerts:

            event = (
                db.query(AuditEvent)
                .filter(
                    AuditEvent.id
                    == int(alert.entity_id)
                )
                .first()
            )

            if (
                event
                and event.created_at
                and event.created_at.year < 2026
            ):
                alert.status = "resolved"
                resolved += 1

        db.commit()

        print(
            f"Resolved {resolved} legacy audit alerts."
        )

    finally:

        db.close()


if __name__ == "__main__":
    run()