from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.analytics.workspace_analytics_builder import (
    build_workspace_analytics_context,
)

from app.services.analytics.workspace_analytics_models import (
    WorkspaceAnalyticsContext,
)


def get_workspace_analytics_context(
    *,
    db: Session,
    workspace_id: int,
) -> WorkspaceAnalyticsContext:
    """
    Institutional Analytics Layer.

    This is the ONLY public entry point for
    workspace analytics inside Trading Truth
    Layer.

    Every analytical surface should consume
    this service rather than rebuilding
    workspace, claim or member metrics
    independently.

    Consumers include:

        - Leaderboard
        - Risk Analytics
        - Due Diligence Reports
        - Verification Analytics
        - Public Claims
        - Allocator Reports
        - Future Commercial Analytics

    Analytics are computed exactly once per
    workspace request and exposed through a
    canonical analytics context object.
    """

    return build_workspace_analytics_context(

        db=db,

        workspace_id=workspace_id,

    )