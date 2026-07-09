from app.models.claim_schema import ClaimSchema


def fetch_workspace_public_claims(
    db,
    workspace_id,
):
    """
    Fetch all claims belonging to a workspace.

    No business logic.
    No filtering.
    No metrics.
    """

    return (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
        )
        .order_by(
            ClaimSchema.id.desc()
        )
        .all()
    )