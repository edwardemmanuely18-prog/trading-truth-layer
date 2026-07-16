from __future__ import annotations

import json

from datetime import datetime

from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema

from app.services.claims.workspace_trade_cache_service import (
    WorkspaceTradeCache,
)


def parse_period_start(
    date_str: str | None,
):

    if not date_str:
        return None

    try:

        return datetime.fromisoformat(
            date_str,
        )

    except Exception:

        return None


def parse_period_end(
    date_str: str | None,
):

    if not date_str:
        return None

    try:

        return datetime.fromisoformat(
            date_str,
        )

    except Exception:

        return None


def coerce_trade_opened_at(
    value,
):

    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):

        return value

    text = str(
        value,
    ).strip()

    candidates = [

        text,

        text.replace(
            "Z",
            "+00:00",
        ),

        text.replace(
            " ",
            "T",
        ),

    ]

    for candidate in candidates:

        try:

            return datetime.fromisoformat(
                candidate,
            )

        except ValueError:

            continue

    return None


def resolve_claim_trades_from_cache(
    *,
    claim: ClaimSchema,
    cache: WorkspaceTradeCache,
) -> list[Trade]:

    included_members = json.loads(
        claim.included_member_ids_json or "[]"
    )

    included_symbols = [

        symbol.upper()

        for symbol in json.loads(
            claim.included_symbols_json or "[]"
        )

    ]

    excluded_trade_ids = set(
        json.loads(
            claim.excluded_trade_ids_json or "[]"
        )
    )

    period_start = parse_period_start(
        claim.period_start,
    )

    period_end = parse_period_end(
        claim.period_end,
    )

    #
    # --------------------------------------------------------
    # Initial trade set.
    # --------------------------------------------------------
    #

    candidate_trades = (
        cache.normalized_workspace_trades
    )

    #
    # --------------------------------------------------------
    # Member filtering.
    # --------------------------------------------------------
    #

    if included_members:

        member_trades = []

        for member_id in included_members:

            member_trades.extend(

                cache.member_index.get(
                    member_id,
                    [],
                )

            )

        candidate_trades = member_trades

    #
    # --------------------------------------------------------
    # Symbol filtering.
    # --------------------------------------------------------
    #

    if included_symbols:

        symbol_filtered = []

        symbol_set = set(
            included_symbols,
        )

        for trade in candidate_trades:

            if (

                (trade.symbol or "").upper()

                in

                symbol_set

            ):

                symbol_filtered.append(
                    trade,
                )

        candidate_trades = symbol_filtered

    #
    # --------------------------------------------------------
    # Period + exclusion filtering.
    # --------------------------------------------------------
    #

    filtered_trades = []

    for trade in candidate_trades:

        trade_dt = coerce_trade_opened_at(
            trade.opened_at,
        )

        if (

            period_start is not None

            and

            (
                trade_dt is None
                or
                trade_dt < period_start
            )

        ):

            continue

        if (

            period_end is not None

            and

            (
                trade_dt is None
                or
                trade_dt >= period_end
            )

        ):

            continue

        if trade.id in excluded_trade_ids:

            continue

        filtered_trades.append(
            trade,
        )

    return filtered_trades