from app.api.routes.claim_schemas import (
    can_show_in_public_directory,
)

from .query_service import (
    fetch_workspace_public_claims,
)


def build_workspace_public_summary(
    db,
    workspace_id,
):
    """
    Workspace-level counters.

    Computed once.

    Future versions will replace this with
    aggregate SQL.
    """

    rows = fetch_workspace_public_claims(
        db,
        workspace_id,
    )

    public_rows = [
        row
        for row in rows
        if can_show_in_public_directory(row)
    ]

    return {
        "total_claims": len(rows),
        "public_claims": len(public_rows),
    }