from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.claim_schema import ClaimSchema

router = APIRouter(prefix="/verify", tags=["verify"])


@router.get("/{claim_hash}")
def verify_claim(claim_hash: str, db: Session = Depends(get_db)):
    claim = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.claim_hash == claim_hash)
        .first()
    )

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Integrity check (simple version for now)
    integrity = "valid" if claim.is_locked else "unverified"

    return {
        "claim_id": claim.id,
        "status": claim.status,
        "is_locked": claim.is_locked,
        "integrity": integrity,
        "workspace_id": claim.workspace_id,
        "created_at": claim.created_at,
        "locked_at": claim.locked_at,
        "published_at": claim.published_at,
        "claim_hash": claim.claim_hash,
        "trade_set_hash": claim.trade_set_hash,
    }