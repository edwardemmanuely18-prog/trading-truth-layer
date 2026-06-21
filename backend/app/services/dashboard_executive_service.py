from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema
from app.models.integrity_alert import IntegrityAlert
from app.models.workspace_membership import WorkspaceMembership


def get_dashboard_executive_summary(
    db: Session,
    workspace_id: int,
):
    return {
        "workspace": {
            "members":
                db.query(
                    func.count(
                        WorkspaceMembership.user_id
                    )
                )
                .filter(
                    WorkspaceMembership.workspace_id
                    == workspace_id
                )
                .scalar() or 0,

            "trades":
                db.query(
                    func.count(Trade.id)
                )
                .filter(
                    Trade.workspace_id
                    == workspace_id
                )
                .scalar() or 0,

            "claims":
                db.query(
                    func.count(
                        ClaimSchema.id
                    )
                )
                .filter(
                    ClaimSchema.workspace_id
                    == workspace_id
                )
                .scalar() or 0,
        },

        "integrity": {
            "alerts":
                db.query(
                    func.count(
                        IntegrityAlert.id
                    )
                )
                .filter(
                    IntegrityAlert.workspace_id
                    == workspace_id,

                    IntegrityAlert.status
                    == "open",
                )
                .scalar() or 0,
        },
    }