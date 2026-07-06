from app.core.db import SessionLocal

from app.models.claim_schema import ClaimSchema

from app.services.claim_service import (
    compute_claim_hash,
)


def run():

    db = SessionLocal()

    try:

        claims = (
            db.query(ClaimSchema)
            .all()
        )

        updated = 0

        for claim in claims:

            new_hash = (
                compute_claim_hash(
                    claim
                )
            )

            if claim.claim_hash != new_hash:

                claim.claim_hash = (
                    new_hash
                )

                updated += 1

                print(
                    f"Rehashed claim "
                    f"{claim.id}"
                )

        db.commit()

        print(
            f"\nUpdated {updated} claims."
        )

    finally:

        db.close()


if __name__ == "__main__":
    run()