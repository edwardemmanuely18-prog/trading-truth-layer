from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.claim_schema import ClaimSchema
from app.api.routes.claim_schemas import (
    compute_claim_hash,
    compute_trade_set_hash,
    resolve_schema_trade_scope,
    resolve_claim_integrity_status,
    coerce_trade_opened_at,
)
from app.models.trade import Trade
import json

router = APIRouter(prefix="/verify", tags=["verify"])

VERIFY_PAYLOAD_VERSION = "phase7.v1"
VERIFY_ISSUER = "Trading Truth Layer"
VERIFY_NETWORK = "trading-truth-layer"
VERIFY_ENDPOINT_KIND = "canonical_verification_route"


def resolve_verification_exposure(claim: ClaimSchema) -> str:
    visibility = str(getattr(claim, "visibility", "") or "").strip().lower()
    status = str(getattr(claim, "status", "") or "").strip().lower()

    if visibility == "public":
        return "public"
    if visibility == "unlisted":
        return "unlisted"
    if status in {"locked", "published", "verified"}:
        return "external_distribution"
    return "internal_only"


def resolve_locked_verification_trades(claim: ClaimSchema, db: Session):
    locked_trade_ids = json.loads(getattr(claim, "locked_trade_ids_json", "[]") or "[]")

    if locked_trade_ids:
        trades = (
            db.query(Trade)
            .filter(Trade.id.in_(locked_trade_ids))
            .all()
        )
        trades = sorted(
            trades,
            key=lambda t: (
                coerce_trade_opened_at(getattr(t, "opened_at", None)) or datetime.min,
                t.id,
            ),
        )
        return trades

    scope = resolve_schema_trade_scope(claim, db)
    return sorted(
        scope["included"],
        key=lambda t: (
            coerce_trade_opened_at(getattr(t, "opened_at", None)) or datetime.min,
            t.id,
        ),
    )


def build_verify_payload(claim: ClaimSchema, db: Session):
    computed_hash = compute_claim_hash(claim)
    live_scope = resolve_schema_trade_scope(claim, db)
    verification_trades = resolve_locked_verification_trades(claim, db)

    stored_trade_set_hash = claim.locked_trade_set_hash
    recomputed_trade_set_hash = compute_trade_set_hash(verification_trades) if verification_trades else None
    exposure_level = resolve_verification_exposure(claim)

    if str(claim.status or "").lower() != "locked":
        integrity = "unlocked"
    elif not stored_trade_set_hash:
        integrity = "compromised"
    elif stored_trade_set_hash == recomputed_trade_set_hash:
        integrity = "valid"
    else:
        integrity = "compromised"

    verify_path = f"/verify/{computed_hash}"
    public_view_path = f"/claim/{claim.id}/public"

    integrity_valid = bool(
        integrity == "valid"
        or (
            stored_trade_set_hash
            and recomputed_trade_set_hash
            and stored_trade_set_hash == recomputed_trade_set_hash
        )
    )

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
        "public_view_path": public_view_path,
        "verify_path": verify_path,

        "payload_version": VERIFY_PAYLOAD_VERSION,
        "issuer": {
            "name": VERIFY_ISSUER,
            "network": VERIFY_NETWORK,
            "endpoint_kind": VERIFY_ENDPOINT_KIND,
        },
        "network_identity": {
            "claim_hash": computed_hash,
            "claim_id": claim.id,
            "workspace_id": claim.workspace_id,
            "verify_path": verify_path,
            "public_view_path": public_view_path,
            "exposure_level": exposure_level,
        },
        "verification_record": {
            "name": claim.name,
            "status": claim.status,
            "visibility": claim.visibility,
            "version_number": claim.version_number,
            "root_claim_id": claim.root_claim_id,
            "parent_claim_id": claim.parent_claim_id,
        },
        "scope": {
            "period_start": claim.period_start,
            "period_end": claim.period_end,
            "included_trade_count": len(live_scope["included"]),
            "excluded_trade_count": len(live_scope["excluded"]),
            "included_member_ids": sorted(
                list(
                    {
                        trade.member_id
                        for trade in live_scope["included"]
                        if getattr(trade, "member_id", None) is not None
                    }
                )
            ),
            "included_symbols": sorted(
                list(
                    {
                        str(trade.symbol)
                        for trade in live_scope["included"]
                        if getattr(trade, "symbol", None)
                    }
                )
            ),
        },
        "integrity_record": {
            "status": integrity,
            "is_valid": integrity_valid,
            "stored_trade_set_hash": stored_trade_set_hash,
            "recomputed_trade_set_hash": recomputed_trade_set_hash,
        },
        "lifecycle": {
            "verified_at": claim.verified_at,
            "published_at": claim.published_at,
            "locked_at": claim.locked_at,
        },
        "proof_summary": {
            "claim_hash": computed_hash,
            "trade_set_hash": stored_trade_set_hash,
            "integrity_status": integrity,
            "integrity_valid": integrity_valid,
            "canonical": True,
            "portable": True,
            "api_addressable": True,
        },
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
                "payload_version": payload["payload_version"],
                "exposure_level": payload["network_identity"]["exposure_level"],
            }
        )

    return {
        "count": len(items),
        "payload_version": VERIFY_PAYLOAD_VERSION,
        "claims": items,
    }


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

    claim = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.claim_hash == claim_hash)
        .first()
    )

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return build_verify_payload(claim, db)