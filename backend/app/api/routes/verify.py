from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.claim_schema import ClaimSchema
from app.api.routes.claim_schemas import (
    compute_claim_hash,
    compute_trade_set_hash,
    resolve_schema_trade_scope,
)

router = APIRouter(prefix="/verify", tags=["verify"])


def build_verify_payload(claim: ClaimSchema, db: Session):
    computed_hash = compute_claim_hash(claim)
    scope = resolve_schema_trade_scope(claim, db)

    stored_trade_set_hash = claim.locked_trade_set_hash
    recomputed_trade_set_hash = compute_trade_set_hash(scope["included"])

    if claim.status == "locked":
        integrity = (
            "valid"
            if stored_trade_set_hash and stored_trade_set_hash == recomputed_trade_set_hash
            else "compromised"
        )
    else:
        integrity = "unlocked"

    return {
        "claim_id": claim.id,
        "workspace_id": claim.workspace_id,
        "name": claim.name,
        "status": claim.status,
        "visibility": claim.visibility,
        "claim_hash": computed_hash,
        "stored_trade_set_hash": stored_trade_set_hash,
        "recomputed_trade_set_hash": recomputed_trade_set_hash,
        "integrity": integrity,
        "version_number": claim.version_number,
        "root_claim_id": claim.root_claim_id,
        "parent_claim_id": claim.parent_claim_id,
        "published_at": claim.published_at,
        "verified_at": claim.verified_at,
        "locked_at": claim.locked_at,
        "period_start": claim.period_start,
        "period_end": claim.period_end,
        "public_view_path": f"/claim/{claim.id}/public",
        "verify_path": f"/verify/{computed_hash}",
    }


@router.get("/debug/all")
def debug_all_claim_hashes(db: Session = Depends(get_db)):
    claims = db.query(ClaimSchema).order_by(ClaimSchema.id.desc()).all()

    items = []
    for claim in claims:
        payload = build_verify_payload(claim, db)
        items.append(
            {
                "id": payload["claim_id"],
                "name": payload["name"],
                "status": payload["status"],
                "workspace_id": payload["workspace_id"],
                "computed_hash": payload["claim_hash"],
                "verify_path": payload["verify_path"],
                "public_view_path": payload["public_view_path"],
            }
        )

    return {"count": len(items), "claims": items}


@router.get("/by-id/{claim_id}")
def verify_claim_by_id(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(ClaimSchema).filter(ClaimSchema.id == claim_id).first()

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return build_verify_payload(claim, db)


@router.get("/{claim_hash}")
def verify_claim(claim_hash: str, db: Session = Depends(get_db)):
    claim_hash = str(claim_hash or "").strip()
    if not claim_hash:
        raise HTTPException(status_code=404, detail="Claim not found")

    claims = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.status.in_(["published", "locked"]))
        .order_by(ClaimSchema.id.desc())
        .all()
    )

    for claim in claims:
        payload = build_verify_payload(claim, db)
        if payload["claim_hash"] == claim_hash:
            return payload

    raise HTTPException(status_code=404, detail="Claim not found")