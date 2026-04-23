from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.claim_schema import ClaimSchema
from app.models.workspace import Workspace

router = APIRouter()


def compute_trust_score(claim):
    score = 0

    if claim.integrity_status == "valid":
        score += 40

    if claim.verification_status == "locked":
        score += 20

    trades = getattr(claim, "trade_count", 0) or 0

    if trades >= 50:
        score += 20
    elif trades >= 20:
        score += 15
    elif trades >= 10:
        score += 10
    elif trades > 0:
        score += 5

    if getattr(claim, "verified_at", None):
        score += 10

    if getattr(claim, "visibility", "") == "public":
        score += 10

    return min(score, 100)


@router.get("/public/claims")
def get_global_public_claims(
    min_trust: int = 0,
    min_trades: int = 0,
    sort_by: str = "trust",
    db: Session = Depends(get_db),
):
    claims = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.visibility == "public")
        .all()
    )

    enriched = []

    for c in claims:
        trust = compute_trust_score(c)

        if trust < min_trust:
            continue

        if (c.trade_count or 0) < min_trades:
            continue

        enriched.append({
            "id": c.id,
            "workspace_id": c.workspace_id,
            "net_pnl": c.net_pnl or 0,
            "trade_count": c.trade_count or 0,
            "trust_score": trust,
        })

    # SORTING ENGINE
    if sort_by == "pnl":
        ranked = sorted(enriched, key=lambda x: x["net_pnl"], reverse=True)
    elif sort_by == "trades":
        ranked = sorted(enriched, key=lambda x: x["trade_count"], reverse=True)
    else:
        ranked = sorted(
            enriched,
            key=lambda x: (x["trust_score"], x["net_pnl"]),
            reverse=True
        )

    # ASSIGN RANK + TIER
    for i, row in enumerate(ranked):
        row["rank"] = i + 1

        score = row["trust_score"]
        if score >= 80:
            row["tier"] = "gold"
        elif score >= 60:
            row["tier"] = "silver"
        elif score >= 40:
            row["tier"] = "bronze"
        else:
            row["tier"] = "unranked"

    return ranked


@router.get("/public/profile/{workspace_id}")
def get_public_profile(
    workspace_id: int,
    db: Session = Depends(get_db)
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()

    if not workspace:
        return {"error": "Workspace not found"}

    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.visibility == "public",
        )
        .all()
    )

    enriched = []

    total_trust = 0
    total_pnl = 0
    total_trades = 0

    for c in claims:
        trust = compute_trust_score(c)

        enriched.append({
            "id": c.id,
            "net_pnl": c.net_pnl or 0,
            "trade_count": c.trade_count or 0,
            "trust_score": trust,
        })

        total_trust += trust
        total_pnl += c.net_pnl or 0
        total_trades += c.trade_count or 0

    ranked = sorted(
        enriched,
        key=lambda x: (x["trust_score"], x["net_pnl"]),
        reverse=True
    )

    for i, row in enumerate(ranked):
        row["rank"] = i + 1

    claim_count = len(ranked)
    avg_trust = total_trust / claim_count if claim_count else 0

    return {
        "workspace_id": workspace.id,
        "name": workspace.name or f"Workspace {workspace.id}",  # ✅ FIX
        "claims": ranked,
        "stats": {
            "claim_count": claim_count,
            "avg_trust": round(avg_trust, 2),
            "total_pnl": total_pnl,
            "total_trades": total_trades,
        },
    }


@router.get("/public/claim/{claim_id}")
def get_public_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.id == claim_id,
            ClaimSchema.visibility == "public"
        )
        .first()
    )

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return {
        "id": claim.id,
        "workspace_id": claim.workspace_id,
        "net_pnl": claim.net_pnl,
        "trade_count": claim.trade_count,
        "trust_score": compute_trust_score(claim),
        "created_at": claim.created_at,
        "verification_status": claim.verification_status,
        "integrity_status": claim.integrity_status,
    }    


@router.get("/verify/{claim_hash}")
def verify_claim_by_hash(claim_hash: str, db: Session = Depends(get_db)):
    claim = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.claim_hash == claim_hash)
        .first()
    )

    if not claim:
        return {"error": "Claim not found"}

    if claim.visibility != "public":
        return {"error": "Claim not public"}

    trust = compute_trust_score(claim)

    workspace = db.query(Workspace).filter(Workspace.id == claim.workspace_id).first()

    return {
        "claim_hash": claim.claim_hash,
        "workspace_id": claim.workspace_id,
        "name": workspace.name if workspace else f"Workspace {claim.workspace_id}",
        "net_pnl": claim.net_pnl,
        "trade_count": claim.trade_count,
        "integrity_status": claim.integrity_status,
        "verification_status": claim.verification_status,
        "trust_score": trust,
        "verified_at": claim.verified_at,
        "created_at": claim.created_at,
    }
