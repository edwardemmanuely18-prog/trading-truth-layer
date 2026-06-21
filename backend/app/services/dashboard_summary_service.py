from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema
from app.models.workspace_membership import WorkspaceMembership
from app.models.integrity_alert import IntegrityAlert


def build_dashboard_summary(
    db: Session,
    workspace_id: int,
):
    trade_count = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id
        )
        .count()
    )

    member_count = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id
            == workspace_id
        )
        .count()
    )

    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    active_alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id
            == workspace_id
        )
        .count()
    )

    return {
        "trade_count": trade_count,
        "member_count": member_count,
        "claim_count": len(claims),

        "draft_claims":
            len(
                [c for c in claims
                 if c.status == "draft"]
            ),

        "verified_claims":
            len(
                [c for c in claims
                 if c.status == "verified"]
            ),

        "published_claims":
            len(
                [c for c in claims
                 if c.status == "published"]
            ),

        "locked_claims":
            len(
                [c for c in claims
                 if c.status == "locked"]
            ),

        "active_alerts":
            active_alerts,
    }