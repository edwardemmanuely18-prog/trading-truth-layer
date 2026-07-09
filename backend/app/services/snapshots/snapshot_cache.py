from __future__ import annotations

from threading import Lock


#
# Temporary in-memory cache.
#
# Later this becomes Redis or Postgres.
#

_claim_cache = {}

_workspace_cache = {}

_lock = Lock()


# ==========================================================
# CLAIM
# ==========================================================


def get_claim_snapshot(
    claim_id: int,
):
    return _claim_cache.get(claim_id)


def store_claim_snapshot(
    claim_id: int,
    snapshot,
):
    with _lock:

        _claim_cache[
            claim_id
        ] = snapshot


def invalidate_claim_snapshot(
    claim_id: int,
):
    with _lock:

        _claim_cache.pop(
            claim_id,
            None,
        )


# ==========================================================
# WORKSPACE
# ==========================================================


def get_workspace_snapshot(
    workspace_id: int,
):
    return _workspace_cache.get(
        workspace_id
    )


def store_workspace_snapshot(
    workspace_id: int,
    snapshot,
):
    with _lock:

        _workspace_cache[
            workspace_id
        ] = snapshot


def invalidate_workspace_snapshot(
    workspace_id: int,
):
    with _lock:

        _workspace_cache.pop(
            workspace_id,
            None,
        )


def clear_snapshot_cache():
    with _lock:

        _claim_cache.clear()

        _workspace_cache.clear()