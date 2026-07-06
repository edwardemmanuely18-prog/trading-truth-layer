from __future__ import annotations

"""
Trading Truth Layer
Trading Performance System (TPS)

Canonical public entry point for trading
performance throughout Trading Truth Layer.

This service is the ONLY entry point that
should be consumed by:

    • Claim Report PDF

    • Allocator Report PDF

    • Dashboard

    • Public Claim

    • Workspace APIs

    • Claim APIs

No consumer should compute trading metrics
directly.

No consumer should assemble performance
objects manually.
"""

from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from app.services.performance.claim_performance import (
    build_claim_performance_metrics,
)

from app.services.performance.workspace_performance import (
    build_workspace_performance_metrics,
)


# ============================================================
# INTERNAL ANALYTICS ENTRY POINT
# ============================================================

def _build_claim_analytics(
    db: Session,
    claim: ClaimSchema,
) -> dict:
    """
    Internal analytics adapter.

    Temporary implementation.

    During migration this function adapts the
    existing analytics layer into the canonical
    TPS contract.

    Eventually this will call the institutional
    analytics engine directly.
    """

    #
    # --------------------------------------------------------
    # TODO
    #
    # Replace with canonical analytics engine.
    #
    # For now we return an empty payload so
    # downstream contracts remain stable.
    #
    # --------------------------------------------------------
    #

    return {}


# ============================================================
# CLAIM PERFORMANCE
# ============================================================

def get_claim_performance_metrics(
    db: Session,
    claim: ClaimSchema,
):
    """
    Canonical single-claim performance.

    Every single-claim consumer inside TTL
    should call this function.

    No consumer should compute trading metrics
    independently.
    """

    analytics = _build_claim_analytics(
        db=db,
        claim=claim,
    )

    return build_claim_performance_metrics(

        claim_schema_id=claim.id,

        workspace_id=claim.workspace_id,

        analytics=analytics,

    )


# ============================================================
# WORKSPACE PERFORMANCE
# ============================================================

def get_workspace_performance_metrics(
    db: Session,
    workspace_id: int,
):
    """
    Canonical workspace performance.

    This aggregates workspace analytics into
    the canonical WorkspacePerformanceMetrics
    contract.
    """

    #
    # --------------------------------------------------------
    # TODO
    #
    # Replace with canonical workspace analytics.
    #
    # --------------------------------------------------------
    #

    analytics = {}

    return build_workspace_performance_metrics(

        workspace_id=workspace_id,

        analytics=analytics,

    )