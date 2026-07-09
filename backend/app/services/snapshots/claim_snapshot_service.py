from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from .snapshot_builder import (
    build_claim_snapshot,
)


# ============================================================
# TEMPORARY IN-MEMORY CACHE
# ============================================================

#
# During development we keep snapshots in memory.
#
# Later this becomes Redis or a Snapshot table.
#

_CLAIM_CACHE: dict[int, dict] = {}


# ============================================================
# PUBLIC API
# ============================================================

def get_claim_snapshot(
    db: Session,
    claim: ClaimSchema,
):
    """
    Canonical entry point.

    Every page should eventually obtain
    claim data through this function.
    """

    cached = _CLAIM_CACHE.get(claim.id)

    if cached is not None:
        return cached

    snapshot = build_claim_snapshot(
        db=db,
        claim=claim,
    )

    _CLAIM_CACHE[claim.id] = snapshot

    return snapshot


# ============================================================
# CACHE MANAGEMENT
# ============================================================

def invalidate_claim_snapshot(
    claim_id: int,
):
    """
    Removes a cached snapshot.

    Called whenever a claim changes.
    """

    _CLAIM_CACHE.pop(
        claim_id,
        None,
    )


def invalidate_workspace_snapshots(
    workspace_id: int,
):
    """
    Temporary implementation.

    Later we'll keep an index by workspace.

    For now we simply clear the cache.
    """

    _CLAIM_CACHE.clear()


def clear_snapshot_cache():
    """
    Development helper.
    """

    _CLAIM_CACHE.clear()


def snapshot_cache_size():

    return len(_CLAIM_CACHE)