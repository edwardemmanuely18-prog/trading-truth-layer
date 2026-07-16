from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema

from app.services.currency.trade_normalization_service import (
    TradeNormalizationService,
)

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
)


def get_normalized_workspace_trades(
    *,
    db: Session,
    workspace_id: int,
):

    workspace_trades = (

        db.query(
            Trade,
        )
        .filter(
            Trade.workspace_id == workspace_id
        )
        .all()

    )

    return TradeNormalizationService.normalize(

        db=db,

        workspace_id=workspace_id,

        trades=workspace_trades,

    )


def resolve_normalized_claim_trades(
    *,
    db: Session,
    claim: ClaimSchema,
    normalized_workspace_trades: list[Trade],
):

    return resolve_schema_trades(

        schema=claim,

        db=db,

        workspace_trades=normalized_workspace_trades,

    )


def get_normalized_claim_trades(
    *,
    db: Session,
    claim: ClaimSchema,
):

    normalized_workspace_trades = (

        get_normalized_workspace_trades(

            db=db,

            workspace_id=claim.workspace_id,

        )

    )

    return resolve_normalized_claim_trades(

        db=db,

        claim=claim,

        normalized_workspace_trades=normalized_workspace_trades,

    )