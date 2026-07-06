from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.claim_schema import ClaimSchema
from app.models.workspace import Workspace

# ✅ IMPORT REAL TRUST ENGINE
from app.api.routes.claim_schemas import (
    resolve_claim_integrity_status,
)

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
)

from app.services.verification.verification_service import (
    get_claim_verification_certificate,
    get_claim_verification_metrics,
)

from app.services.trade_metrics_service import (
    compute_trade_metrics,
)

from app.api.routes.claim_schemas import (
    build_public_claim_payload,
)

router = APIRouter()


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
        payload = build_public_claim_payload(
            schema=c,
            db=db,
        )

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
        payload = build_public_claim_payload(
            schema=c,
            db=db,
        )

        rows.append(
            {
                "claim_id": c.id,
                "workspace_id": c.workspace_id,
                "trust_score": payload["verification"]["score"],
                "net_pnl": payload["net_pnl"],
            }
        )

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
        payload = build_public_claim_payload(
            schema=c,
            db=db,
        )

        verification = payload["verification"]

        total_trust += verification["score"]
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

    return build_public_claim_payload(
        schema=claim,
        db=db,
    )


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


    payload = build_public_claim_payload(
        schema=claim,
        db=db,
    )

    return {
        **payload,
        "verification_result": "verified",
    }