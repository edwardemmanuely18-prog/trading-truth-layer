from sqlalchemy.orm import Session

from app.models.claim import Claim


def get_workspace_leaderboard(
    db: Session,
    workspace_id: int,
):
    claims = (
        db.query(Claim)
        .filter(
            Claim.workspace_id == workspace_id
        )
        .all()
    )

    claim_rankings = []

    for claim in claims:
        claim_rankings.append(
            {
                "claim_schema_id":
                    claim.claim_schema_id,

                "name":
                    claim.name,

                "trade_count":
                    claim.trade_count,

                "net_pnl":
                    claim.net_pnl,

                "profit_factor":
                    claim.profit_factor,

                "win_rate":
                    claim.win_rate,

                "verification_status":
                    claim.verification_status,
            }
        )

    claim_rankings.sort(
        key=lambda x:
        x["net_pnl"] or 0,
        reverse=True,
    )

    return {
        "summary": {
            "claim_count":
                len(claim_rankings),
        },

        "claim_rankings":
            claim_rankings,

        "member_rankings": [],
    }