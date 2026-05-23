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

router = APIRouter(
    prefix="/public",
    tags=["public"]
)


# =========================
# 🌐 CANONICAL PUBLIC CLAIM PAYLOAD
# =========================
def build_public_claim_payload(
    claim,
    db: Session,
):
    trust, metrics = compute_full_trust(claim, db)

    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == claim.workspace_id)
        .first()
    )

    profile_payload = {
        "profile_id": f"workspace:{claim.workspace_id}",
        "workspace_id": claim.workspace_id,
        "name": workspace.name if workspace else f"Workspace {claim.workspace_id}",
        "type": "workspace",
        "network": "internal",
        "claims_count": 0,
        "locked_claims_count": 0,
        "contested_claims_count": 0,
        "average_trust_score": trust,
        "average_network_score": 0,
        "total_net_pnl": metrics.get("net_pnl", 0),
        "trust_profile_band":
            "high"
            if trust >= 80
            else "moderate"
            if trust >= 60
            else "developing",
    }

    return {
        # =========================
        # CORE IDENTIFIERS
        # =========================
        "claim_schema_id": claim.id,
        "claim_hash": claim.claim_hash,
        "workspace_id": claim.workspace_id,

        # =========================
        # CANONICAL ROUTES
        # =========================
        "public_view_path": f"/claim/{claim.id}/public",
        "verify_path": f"/verify/{claim.claim_hash}",

        # =========================
        # CORE CLAIM
        # =========================
        "name": getattr(claim, "name", f"Claim {claim.id}"),

        # =========================
        # ISSUER
        # =========================
        "issuer": {
            "id": claim.workspace_id,
            "name": workspace.name if workspace else f"Workspace {claim.workspace_id}",
            "type": "workspace",
            "network": "internal",
            "profile": profile_payload,
        },

        # =========================
        # PROFILE
        # =========================
        "profile": profile_payload,

        # =========================
        # VISIBILITY + SCOPE
        # =========================
        "scope": {
            "visibility": claim.visibility,
            "period_start": None,
            "period_end": None,
            "included_members": [],
            "included_symbols": [],
            "methodology_notes": "",
        },

        # =========================
        # LIFECYCLE
        # =========================
        "lifecycle": {
            "status": getattr(claim, "status", "unknown"),
            "verified_at": getattr(claim, "verified_at", None),
            "published_at": getattr(claim, "published_at", None),
            "locked_at": getattr(claim, "locked_at", None),
        },

        # =========================
        # COMPATIBILITY
        # =========================
        "verification_status": getattr(claim, "status", "unknown"),

        # =========================
        # PERFORMANCE
        # =========================
        "trade_count": metrics.get("trade_count", 0),
        "net_pnl": metrics.get("net_pnl", 0),
        "profit_factor": metrics.get("profit_factor", 0),
        "win_rate": metrics.get("win_rate", 0),

        # =========================
        # TRUST
        # =========================
        "trust_score": trust,

        # =========================
        # LEADERBOARD
        # =========================
        "leaderboard": [],

        # =========================
        # PUBLIC STATE
        # =========================
        "is_publicly_accessible": (
            claim.visibility == "public"
            and getattr(claim, "status", "") == "locked"
        ),
    }


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
def get_public_claims(
    min_trust: float = 0,
    min_trades: int = 0,
    sort_by: str = "trust",
    db: Session = Depends(get_db),
):
    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.visibility == "public",
            ClaimSchema.status == "locked",
        )
        .all()
    )

    enriched = []

    for c in claims:
        payload = build_public_claim_payload(c, db)

        if payload["trust_score"] < min_trust:
            continue

        if payload["trade_count"] < min_trades:
            continue

        enriched.append(payload)

    # SORTING ENGINE
    if sort_by == "pnl":
        ranked = sorted(
            enriched,
            key=lambda x: x["net_pnl"],
            reverse=True
        )
    elif sort_by == "trades":
        ranked = sorted(
            enriched,
            key=lambda x: x["trade_count"],
            reverse=True
        )
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
        else:
            row["tier"] = "bronze"

    return ranked


# =========================
# 🏆 GLOBAL LEADERBOARD
# =========================
@router.get("/public/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.visibility == "public",
            ClaimSchema.status == "locked"
        )
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
            ClaimSchema.status == "locked",
        )
        .all()
    )

    enriched = []

    total_trust = 0
    total_pnl = 0
    total_trades = 0

    for c in claims:
        trust, metrics = compute_full_trust(c, db)

        payload = build_public_claim_payload(c, db)

        enriched.append(payload)

        total_trust += payload["trust_score"]
        total_pnl += payload["net_pnl"]
        total_trades += payload["trade_count"]

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
def get_public_claim(
    claim_id: int,
    db: Session = Depends(get_db)
):
    claim = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.id == claim_id,
            ClaimSchema.visibility == "public",
            ClaimSchema.status == "locked",
        )
        .first()
    )

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Public claim not found"
        )

    return build_public_claim_payload(claim, db)


# =========================
# 🔍 VERIFY CLAIM BY HASH
# =========================
@router.get("/verify/{claim_hash}")
def verify_claim_by_hash(claim_hash: str, db: Session = Depends(get_db)):
    claim = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.claim_hash == claim_hash,
            ClaimSchema.visibility == "public",
            ClaimSchema.status == "locked",
        )
        .first()
    )

    if not claim:
        raise HTTPException(
            status_code=404,
            detail="Public claim not found for supplied hash"
        )


    payload = build_public_claim_payload(claim, db)

    return {
        **payload,
        "verification_result": "verified",
    }