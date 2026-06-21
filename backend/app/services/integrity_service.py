import json
import hashlib

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema

from app.services.claim_service import (
    compute_claim_hash,
)

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
    compute_trade_set_hash,
)



def verify_claim_integrity(
    schema,
    db,
):
    trades = resolve_schema_trades(
        schema,
        db,
    )

    current_trade_hash = (
        compute_trade_set_hash(
            trades
        )
    )

    if (
        schema.locked_trade_set_hash
        and current_trade_hash
        != schema.locked_trade_set_hash
    ):
        return {
            "valid": False,
            "message":
                "Trade set hash mismatch.",
        }

    current_claim_hash = (
        compute_claim_hash(
            schema
        )
    )

    if (
        schema.claim_hash
        and current_claim_hash
        != schema.claim_hash
    ):
        return {
            "valid": False,
            "message":
                "Claim hash mismatch.",
        }

    return {
        "valid": True,
        "message": None,
    }
