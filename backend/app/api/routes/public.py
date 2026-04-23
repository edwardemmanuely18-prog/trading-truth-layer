from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.claim_schema import ClaimSchema
from app.models.workspace import Workspace

# ✅ IMPORT REAL TRUST ENGINE
from app.api.routes.claim_schemas import (
    compute_backend_trust_score,
    resolve_schema_trades,
    compute_trade_metrics,
    resolve_claim_dispute_context,
    resolve_claim_integrity_status,
)

router = APIRouter()


# =========================
# 🧠 TRUST COMPUTATION CORE
# =========================
def compute_full_trust(claim, db: Session):
    trades = resolve_schema_trades(claim, db)
    metrics = compute_trade_metrics(trades)
    dispute_ctx = resolve_claim_dispute_context(claim, db)
    integrity = resolve_claim_integrity_status(claim, trades)

    trust = compute_backend_trust_score(claim, metrics, integrity, dispute_ctx)

    return trust, metrics


# =========================
# 🌍 GLOBAL CLAIM DIRECTORY
# =========================
@router.get("/public/claims")
def get_global_public_claims(
    min_trust: int = 0,
    min_trades: int = 0,
    sort_by: str = "trust",
    db: Session = Depends(get_db),
):
    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.visibility == "public",
            ClaimSchema.status == "locked"
        )
        .all()
    )

    enriched = []

    for c in claims:
        trust, metrics = compute_full_trust(c, db)

        if trust < min_trust:
            continue

        if (metrics.get("trade_count", 0)) < min_trades:
            continue

        enriched.append({
            "claim_schema_id": c.id,
            "claim_hash": c.claim_hash,

            # 👇 REQUIRED FOR WORKSPACE FILTER
            "issuer": {
                "id": c.workspace_id,
            },

            "profile": {
                "workspace_id": c.workspace_id,
            },

            # 👇 REQUIRED FOR VISIBILITY FILTER
            "scope": {
                "visibility": c.visibility,
                "period_start": None,
                "period_end": None,
                "included_members": [],
                "included_symbols": [],
                "methodology_notes": "",
            },

            # 👇 REQUIRED FOR LOCK FILTER
            "lifecycle": {
                "status": "locked" if getattr(c, "status", "") == "locked" else "unlocked",
                "locked_at": getattr(c, "locked_at", None),
                "verified_at": getattr(c, "verified_at", None),
                "published_at": None,
                "locked_trade_set_hash": None,
            },

            # 👇 CORE DATA
            "name": getattr(c, "name", f"Claim {c.id}"),
            "verification_status": getattr(c, "status", "unknown"),

            "net_pnl": metrics.get("net_pnl", 0),
            "trade_count": metrics.get("trade_count", 0),

            # 👇 ADD THESE (your UI expects them)
            "profit_factor": metrics.get("profit_factor", 0),
            "win_rate": metrics.get("win_rate", 0),

            "trust_score": trust,

            # 👇 REQUIRED FOR MEMBER TABLE (safe empty)
            "leaderboard": [],
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


# =========================
# 🏆 GLOBAL LEADERBOARD
# =========================
@router.get("/public/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    claims = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.visibility == "public")
        .all()
    )

    rows = []

    for c in claims:
        trust, metrics = compute_full_trust(c, db)

        rows.append({
            "claim_id": c.id,
            "workspace_id": c.workspace_id,
            "trust_score": trust,
            "net_pnl": metrics.get("net_pnl", 0),
        })

    ranked = sorted(
        rows,
        key=lambda x: (x["trust_score"], x["net_pnl"]),
        reverse=True
    )

    for i, r in enumerate(ranked):
        r["rank"] = i + 1

    return ranked


# =========================
# 👤 PUBLIC PROFILE
# =========================
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
        trust, metrics = compute_full_trust(c, db)

        enriched.append({
            "id": c.id,
            "net_pnl": metrics.get("net_pnl", 0),
            "trade_count": metrics.get("trade_count", 0),
            "trust_score": trust,
        })

        total_trust += trust
        total_pnl += metrics.get("net_pnl", 0)
        total_trades += metrics.get("trade_count", 0)

    ranked = sorted(
        enriched,
        key=lambda x: (x["trust_score"], x["net_pnl"]),
        reverse=True
    )

    for i, row in enumerate(ranked):
        row["rank"] = i + 1

    claim_count = len(ranked)
    avg_trust = total_trust / claim_count if claim_count else 0

    # 🏆 GET RANK FROM GLOBAL LEADERBOARD
    leaderboard = get_leaderboard(db)

    workspace_rank = next(
        (r["rank"] for r in leaderboard if r["workspace_id"] == workspace_id),
        None
    )

    return {
        "workspace_id": workspace.id,
        "name": workspace.name or f"Workspace {workspace.id}",
        "rank": workspace_rank,  # ✅ NEW
        "claims": ranked,
        "stats": {
            "claim_count": claim_count,
            "avg_trust": round(avg_trust, 2),
            "total_pnl": total_pnl,
            "total_trades": total_trades,
        },
    }


# =========================
# 📄 SINGLE CLAIM
# =========================
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

    trust, metrics = compute_full_trust(claim, db)

    return {
        "id": claim.id,
        "workspace_id": claim.workspace_id,
        "net_pnl": metrics.get("net_pnl", 0),
        "trade_count": metrics.get("trade_count", 0),
        "trust_score": trust,
        "created_at": claim.created_at,
        "verification_status": claim.verification_status,
        "integrity_status": claim.integrity_status,
    }


# =========================
# 🔍 VERIFY CLAIM BY HASH
# =========================
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

    trust, metrics = compute_full_trust(claim, db)

    workspace = db.query(Workspace).filter(Workspace.id == claim.workspace_id).first()

    return {
        "claim_hash": claim.claim_hash,
        "workspace_id": claim.workspace_id,
        "name": workspace.name if workspace else f"Workspace {claim.workspace_id}",
        "net_pnl": metrics.get("net_pnl", 0),
        "trade_count": metrics.get("trade_count", 0),
        "integrity_status": claim.integrity_status,
        "verification_status": claim.verification_status,
        "trust_score": trust,
        "verified_at": claim.verified_at,
        "created_at": claim.created_at,
    }