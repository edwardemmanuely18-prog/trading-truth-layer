from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.claim_schema import ClaimSchema
from app.api.routes.claim_schemas import compute_claim_hash, compute_trade_set_hash, resolve_schema_trade_scope

router = APIRouter(prefix="/verify", tags=["verify"])


@router.get("/{claim_hash}")
def verify_claim(claim_hash: str, db: Session = Depends(get_db)):
    claims = (
        db.query(ClaimSchema)
        .order_by(ClaimSchema.id.desc())
        .all()
    )

    matched_claim = None
    matched_computed_hash = None

    for claim in claims:
        computed_hash = compute_claim_hash(claim)
        if computed_hash == claim_hash:
            matched_claim = claim
            matched_computed_hash = computed_hash
            break

    if not matched_claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    scope = resolve_schema_trade_scope(matched_claim, db)

    stored_trade_set_hash = matched_claim.locked_trade_set_hash
    recomputed_trade_set_hash = compute_trade_set_hash(scope["included"])

    if matched_claim.status == "locked":
        integrity = "valid" if stored_trade_set_hash and stored_trade_set_hash == recomputed_trade_set_hash else "compromised"
    else:
        integrity = "unlocked"


@router.get("/debug/all")
def debug_all_claim_hashes(db: Session = Depends(get_db)):
    claims = db.query(ClaimSchema).order_by(ClaimSchema.id.desc()).all()

    items = []
    for claim in claims:
        try:
            computed_hash = compute_claim_hash(claim)
        except Exception as e:
            computed_hash = f"ERROR: {str(e)}"

        items.append(
            {
                "id": claim.id,
                "name": claim.name,
                "status": claim.status,
                "workspace_id": claim.workspace_id,
                "computed_hash": computed_hash,
                "public_view_path": f"/claim/{claim.id}/public",
            }
        )

    return {"count": len(items), "claims": items}        

    return {
        "claim_id": matched_claim.id,
        "workspace_id": matched_claim.workspace_id,
        "name": matched_claim.name,
        "status": matched_claim.status,
        "visibility": matched_claim.visibility,
        "claim_hash": matched_computed_hash,
        "stored_trade_set_hash": stored_trade_set_hash,
        "recomputed_trade_set_hash": recomputed_trade_set_hash,
        "integrity": integrity,
        "version_number": matched_claim.version_number,
        "root_claim_id": matched_claim.root_claim_id,
        "parent_claim_id": matched_claim.parent_claim_id,
        "published_at": matched_claim.published_at,
        "verified_at": matched_claim.verified_at,
        "locked_at": matched_claim.locked_at,
        "period_start": matched_claim.period_start,
        "period_end": matched_claim.period_end,
        "public_view_path": f"/claim/{matched_claim.id}/public",
        "verify_path": f"/verify/{matched_computed_hash}",
    }