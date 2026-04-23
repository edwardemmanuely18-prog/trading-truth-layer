from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.claim_schema import ClaimSchema

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

    # ✅ SINGLE SOURCE OF TRUTH (ranking)
    if sort_by == "pnl":
        ranked = sorted(
            enriched,
            key=lambda x: x["net_pnl"] or 0,
            reverse=True
        )
    elif sort_by == "trades":
        ranked = sorted(
            enriched,
            key=lambda x: x["trade_count"] or 0,
            reverse=True
        )
    else:
        # default: trust
        ranked = sorted(
            enriched,
            key=lambda x: (x["trust_score"], x["net_pnl"] or 0),
            reverse=True
        )

    # ✅ assign rank AFTER sorting
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

    # ✅ apply limit safely
    return ranked[:limit]