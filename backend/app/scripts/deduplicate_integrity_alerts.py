from app.core.db import SessionLocal
from app.models.integrity_alert import IntegrityAlert


def run():

    db = SessionLocal()

    try:

        alerts = (
            db.query(IntegrityAlert)
            .filter(
                IntegrityAlert.status == "open"
            )
            .order_by(
                IntegrityAlert.id.asc()
            )
            .all()
        )

        seen = set()

        resolved = 0

        for alert in alerts:

            key = (
                alert.alert_type,
                alert.entity_type,
                alert.entity_id,
            )

            if key in seen:

                alert.status = "resolved"
                resolved += 1

            else:

                seen.add(key)

        db.commit()

        print(
            f"Resolved {resolved} duplicate alerts."
        )

    finally:

        db.close()


if __name__ == "__main__":
    run()