from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from .snapshot_builder import (
    build_workspace_snapshot,
)

from .claim_snapshot_service import (
    get_claim_snapshot,
)


# ============================================================
# TEMPORARY CACHE
# ============================================================

_WORKSPACE_CACHE: dict[int, dict] = {}


# ============================================================
# PUBLIC API
# ============================================================

def get_workspace_snapshot(
    db: Session,
    workspace_id: int,
):
    """
    Canonical workspace snapshot.

    Builds expensive workspace information
    only once.
    """

    cached = _WORKSPACE_CACHE.get(
        workspace_id
    )

    if cached is not None:
        return cached

    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .order_by(
            ClaimSchema.id.desc()
        )
        .all()
    )

    snapshot = build_workspace_snapshot(
        db=db,
        workspace_id=workspace_id,
    )

    snapshot["claim_snapshots"] = [

        get_claim_snapshot(
            db=db,
            claim=claim,
        )

        for claim in claims

    ]

    _WORKSPACE_CACHE[
        workspace_id
    ] = snapshot

    return snapshot


# ============================================================
# CACHE MANAGEMENT
# ============================================================

def invalidate_workspace_snapshot(
    workspace_id: int,
):

    _WORKSPACE_CACHE.pop(
        workspace_id,
        None,
    )


def clear_workspace_snapshot_cache():

    _WORKSPACE_CACHE.clear()


def workspace_snapshot_cache_size():

    return len(
        _WORKSPACE_CACHE
    )