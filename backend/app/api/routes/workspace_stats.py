from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.db import get_db
from app.models.claim import Claim
from app.models.trade import Trade

router = APIRouter()

@router.get("/workspace/{workspace_id}/stats")
def get_workspace_stats(workspace_id: int, db: Session = Depends(get_db)):
    total_claims = db.query(func.count(Claim.id)).filter(
        Claim.workspace_id == workspace_id
    ).scalar()

    locked_claims = db.query(func.count(Claim.id)).filter(
        Claim.workspace_id == workspace_id,
        Claim.status == "locked"
    ).scalar()

    public_claims = db.query(func.count(Claim.id)).filter(
        Claim.workspace_id == workspace_id,
        Claim.visibility == "public"
    ).scalar()

    total_trades = db.query(func.count(Trade.id)).filter(
        Trade.workspace_id == workspace_id
    ).scalar()

    recent_claims = db.query(Claim).filter(
        Claim.workspace_id == workspace_id
    ).order_by(Claim.created_at.desc()).limit(5).all()

    return {
        "total_claims": total_claims,
        "locked_claims": locked_claims,
        "public_claims": public_claims,
        "total_trades": total_trades,
        "recent_claims": [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "created_at": c.created_at
            }
            for c in recent_claims
        ]
    }
