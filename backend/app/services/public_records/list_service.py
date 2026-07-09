from app.api.routes.claim_schemas import (
    can_show_in_public_directory,
)

from .query_service import (
    fetch_workspace_public_claims,
)

from .serializers import (
    serialize_public_claim,
)


def build_workspace_public_records(
    db,
    workspace_id,
):
    """
    Canonical Public Records service.

    This replaces route-level orchestration.

    Behaviour intentionally matches the
    existing implementation.
    """

    rows = fetch_workspace_public_claims(
        db,
        workspace_id,
    )

    rows = [
        row
        for row in rows
        if can_show_in_public_directory(row)
    ]

    return [
        serialize_public_claim(
            row,
            db,
        )
        for row in rows
    ]