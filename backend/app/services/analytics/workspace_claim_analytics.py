from __future__ import annotations

import time

from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
)

from app.services.trade_metrics_service import (
    compute_trade_metrics,
)

from app.services.currency.trade_normalization_service import (
    TradeNormalizationService,
)

from app.services.analytics.workspace_analytics_models import (
    WorkspaceClaimAnalytics,
)


def build_workspace_claim_analytics(
    *,
    db: Session,
    workspace_id: int,
    workspace_claims: list[ClaimSchema],
    workspace_trades: list[Trade],
) -> tuple[
    list[WorkspaceClaimAnalytics],
    dict[int, list[Trade]],
    list[Trade],
    str,
]:

    claim_metrics = []

    claim_trade_map = {}

    #
    # Normalize the workspace trades ONCE.
    #

    normalization_start = time.perf_counter()

    normalized_workspace_trades = (

        TradeNormalizationService.normalize(

            db=db,

            workspace_id=workspace_id,

            trades=workspace_trades,

        )

    )

    reporting_currency = (

        TradeNormalizationService
        .get_reporting_currency(

            db=db,

            workspace_id=workspace_id,

        )

    )

    print(
        f"trade normalization = "
        f"{time.perf_counter()-normalization_start:.4f}s"
    )

    #
    # Resolve every claim scope exactly once.
    #

    claim_analytics_total = 0

    for claim in workspace_claims:

        claim_start = time.perf_counter()

        scope_start = time.perf_counter()

        trades = resolve_schema_trades(

            schema=claim,

            db=db,

            workspace_trades=normalized_workspace_trades,

        )

        print(
            f"claim {claim.id} "
            f"scope resolution = "
            f"{time.perf_counter()-scope_start:.4f}s"
        )

        claim_trade_map[claim.id] = trades

        metrics_start = time.perf_counter()

        analytics = compute_trade_metrics(
            trades,
        )

        print(
            f"claim {claim.id} "
            f"trade metrics = "
            f"{time.perf_counter()-metrics_start:.4f}s"
        )

        claim_metrics.append(

            WorkspaceClaimAnalytics(

                claim=claim,

                metrics=analytics,

                trades=trades,

            )

        )

        print(
            f"claim {claim.id} total = "
            f"{time.perf_counter()-claim_start:.4f}s"
        )

        claim_analytics_total += (
            time.perf_counter() - claim_start
        )

    print(
        f"ALL CLAIM ANALYTICS = "
        f"{claim_analytics_total:.4f}s"
    )

    return (

        claim_metrics,

        claim_trade_map,

        normalized_workspace_trades,

        reporting_currency,

    )