from sqlalchemy.orm import Session

from app.core.db import SessionLocal

from app.models.claim_schema import ClaimSchema

from app.services.claim_service import (
    compute_claim_hash,
)

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
    compute_trade_set_hash,
    compute_integrity_snapshot,
)

import json


def run():

    db: Session = SessionLocal()

    try:

        claims = (
            db.query(ClaimSchema)
            .order_by(
                ClaimSchema.id
            )
            .all()
        )

        print(
            f"\nFound {len(claims)} claims\n"
        )

        updated = 0

        for claim in claims:

            changed = False

            trades = (
                resolve_schema_trades(
                    claim,
                    db,
                )
            )

            #
            # CLAIM HASH
            #

            if not claim.claim_hash:

                claim.claim_hash = (
                    compute_claim_hash(
                        claim
                    )
                )

                changed = True

            #
            # TRADE SET HASH
            #

            if not claim.locked_trade_set_hash:

                claim.locked_trade_set_hash = (
                    compute_trade_set_hash(
                        trades
                    )
                )

                changed = True

            #
            # INTEGRITY SNAPSHOT
            #

            if (
                not claim.integrity_snapshot_json
                or
                claim.integrity_snapshot_json == "{}"
            ):

                snapshot = (
                    compute_integrity_snapshot(
                        claim,
                        trades,
                    )
                )

                claim.integrity_snapshot_json = (
                    json.dumps(
                        snapshot
                    )
                )

                claim.scope_hash = (
                    snapshot.get(
                        "scope_hash"
                    )
                )

                claim.lifecycle_hash = (
                    snapshot.get(
                        "lifecycle_hash"
                    )
                )

                changed = True

            if changed:

                updated += 1

                print(
                    f"Updated Claim "
                    f"{claim.id} "
                    f"({claim.name})"
                )

        db.commit()

        print(
            f"\nBackfill Complete"
        )

        print(
            f"Claims Updated: {updated}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    run()