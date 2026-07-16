from __future__ import annotations

import time

from sqlalchemy.orm import Session

from app.models.claim_schema import (
    ClaimSchema,
)

from app.models.trade import (
    Trade,
)

from app.services.analytics.workspace_claim_analytics import (
    build_workspace_claim_analytics,
)

from app.services.analytics.workspace_member_analytics import (
    build_workspace_member_analytics,
)

from app.services.analytics.workspace_metrics_analytics import (
    build_workspace_metrics_analytics,
)

from app.services.analytics.workspace_analytics_models import (
    WorkspaceAnalyticsContext,
)


def build_workspace_analytics_context(
    *,
    db: Session,
    workspace_id: int,
) -> WorkspaceAnalyticsContext:

    start = time.perf_counter()

    #
    # ----------------------------------------------------
    # Load all workspace claims once.
    # ----------------------------------------------------
    #

    claims_start = time.perf_counter()

    workspace_claims = (

        db.query(
            ClaimSchema,
        )
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()

    )

    print(
        f"workspace claims query = "
        f"{time.perf_counter()-claims_start:.4f}s"
    )

    #
    # ----------------------------------------------------
    # Load all workspace trades once.
    # ----------------------------------------------------
    #

    trades_start = time.perf_counter()

    workspace_trades = (

        db.query(
            Trade,
        )
        .filter(
            Trade.workspace_id
            == workspace_id
        )
        .all()

    )

    print(
        f"workspace trades query = "
        f"{time.perf_counter()-trades_start:.4f}s"
    )

    #
    # ----------------------------------------------------
    # Compute claim analytics.
    # ----------------------------------------------------
    #

    claim_analytics_start = time.perf_counter()

    (
        claim_metrics,
        claim_trade_map,
        normalized_workspace_trades,
        reporting_currency,
    ) = (

        build_workspace_claim_analytics(

            db=db,

            workspace_id=workspace_id,

            workspace_claims=workspace_claims,

            workspace_trades=workspace_trades,

        )

    )

    print(
        f"claim analytics = "
        f"{time.perf_counter()-claim_analytics_start:.4f}s"
    )

    #
    # ----------------------------------------------------
    # Compute member analytics.
    # ----------------------------------------------------
    #

    member_start = time.perf_counter()

    member_metrics = (

        build_workspace_member_analytics(

            claim_metrics=claim_metrics,

        )

    )

    print(
        f"member analytics = "
        f"{time.perf_counter()-member_start:.4f}s"
    )

    #
    # ----------------------------------------------------
    # Compute workspace analytics.
    # ----------------------------------------------------
    #

    workspace_metrics_start = time.perf_counter()

    workspace_metrics = (

        build_workspace_metrics_analytics(

            claim_metrics=claim_metrics,

        )

    )

    print(
        f"workspace metrics = "
        f"{time.perf_counter()-workspace_metrics_start:.4f}s"
    )

    #
    # ----------------------------------------------------
    # Build context.
    # ----------------------------------------------------
    #

    print(
        f"workspace analytics TOTAL = "
        f"{time.perf_counter()-start:.4f}s"
    )

    return WorkspaceAnalyticsContext(

        workspace_id=workspace_id,

        reporting_currency=
            reporting_currency,

        workspace_claims=workspace_claims,

        workspace_trades=workspace_trades,

        #
        # Currency normalization is already
        # performed inside the claim analytics
        # layer.
        #

        normalized_workspace_trades=
            normalized_workspace_trades,

        claim_metrics=claim_metrics,

        member_metrics=member_metrics,

        workspace_metrics=workspace_metrics,

        claim_trade_map=claim_trade_map,

    )