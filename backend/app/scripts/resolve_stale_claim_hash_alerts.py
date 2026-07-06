from app.core.db import SessionLocal

from app.models.integrity_alert import (
    IntegrityAlert,
)

from app.models.claim_schema import (
    ClaimSchema,
)

from app.services.claim_service import (
    compute_claim_hash,
)


def run():

    db = SessionLocal()

    try:

        alerts = (
            db.query(IntegrityAlert)
            .filter(
                IntegrityAlert.alert_type
                == "CLAIM_HASH_MISMATCH",

                IntegrityAlert.status
                == "open",
            )
            .all()
        )

        resolved = 0

        for alert in alerts:

            claim = (
                db.query(ClaimSchema)
                .filter(
                    ClaimSchema.id
                    == int(alert.entity_id)
                )
                .first()
            )

            if not claim:
                continue

            current_hash = (
                compute_claim_hash(
                    claim
                )
            )

            if (
                claim.claim_hash
                == current_hash
            ):
                alert.status = "resolved"
                resolved += 1

        db.commit()

        print(
            f"Resolved {resolved} alerts."
        )

    finally:

        db.close()


if __name__ == "__main__":
    run()