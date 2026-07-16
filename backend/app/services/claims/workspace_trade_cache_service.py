from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.trade import Trade

from app.services.currency.trade_normalization_service import (
    TradeNormalizationService,
)


@dataclass
class WorkspaceTradeCache:

    workspace_id: int

    workspace_trades: list[Trade]

    normalized_workspace_trades: list[Trade]

    member_index: dict[int, list[Trade]]

    symbol_index: dict[str, list[Trade]]

    trade_id_index: dict[int, Trade]


def build_workspace_trade_cache(
    *,
    db: Session,
    workspace_id: int,
) -> WorkspaceTradeCache:

    #
    # --------------------------------------------------------
    # Load workspace trades once.
    # --------------------------------------------------------
    #

    workspace_trades = (

        db.query(
            Trade,
        )
        .filter(
            Trade.workspace_id == workspace_id
        )
        .all()

    )

    #
    # --------------------------------------------------------
    # Normalize currencies once.
    # --------------------------------------------------------
    #

    normalized_workspace_trades = (

        TradeNormalizationService.normalize(

            db=db,

            workspace_id=workspace_id,

            trades=workspace_trades,

        )

    )

    #
    # --------------------------------------------------------
    # Build indexes once.
    # --------------------------------------------------------
    #

    member_index = defaultdict(list)

    symbol_index = defaultdict(list)

    trade_id_index = {}

    for trade in normalized_workspace_trades:

        #
        # Member index.
        #

        member_index[
            trade.member_id
        ].append(
            trade,
        )

        #
        # Symbol index.
        #

        symbol_index[
            (trade.symbol or "").upper()
        ].append(
            trade,
        )

        #
        # Trade id index.
        #

        trade_id_index[
            trade.id
        ] = trade

    #
    # --------------------------------------------------------
    # Build cache object.
    # --------------------------------------------------------
    #

    return WorkspaceTradeCache(

        workspace_id=workspace_id,

        workspace_trades=workspace_trades,

        normalized_workspace_trades=normalized_workspace_trades,

        member_index=dict(member_index),

        symbol_index=dict(symbol_index),

        trade_id_index=trade_id_index,

    )