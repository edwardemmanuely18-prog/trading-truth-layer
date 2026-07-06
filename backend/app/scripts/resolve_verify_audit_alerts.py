from app.core.db import SessionLocal

from app.models.integrity_alert import IntegrityAlert


def run():

    db = SessionLocal()

    try:

        alerts = (
            db.query(IntegrityAlert)
            .filter(
                IntegrityAlert.alert_type
                == "VERIFY_AUDIT_MISSING",

                IntegrityAlert.status
                == "open",
            )
            .all()
        )

        for alert in alerts:

            alert.status = "resolved"

        db.commit()

        print(
            f"Resolved {len(alerts)} verify alerts."
        )

    finally:

        db.close()


if __name__ == "__main__":
    run()