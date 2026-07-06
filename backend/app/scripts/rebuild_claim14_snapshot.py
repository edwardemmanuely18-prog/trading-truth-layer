import json

from app.core.db import SessionLocal

from app.models.claim_schema import ClaimSchema

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
    compute_integrity_snapshot,
)


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

        trades = (
            resolve_schema_trades(
                claim,
                db,
            )
        )

        snapshot = (
            compute_integrity_snapshot(
                claim,
                trades,
            )
        )

        claim.integrity_snapshot_json = (
            json.dumps(snapshot)
        )

        db.commit()

        print(
            "Claim 14 snapshot rebuilt."
        )

    finally:

        db.close()


if __name__ == "__main__":
    run()