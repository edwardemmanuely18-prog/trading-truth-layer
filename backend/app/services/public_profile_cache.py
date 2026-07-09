from __future__ import annotations

_PROFILE_CACHE: dict[int, dict] = {}


def get_workspace_public_profile(
    workspace_id: int,
):
    return _PROFILE_CACHE.get(workspace_id)


def store_workspace_public_profile(
    workspace_id: int,
    profile: dict,
):
    _PROFILE_CACHE[workspace_id] = profile


def clear_workspace_public_profile(
    workspace_id: int,
):
    _PROFILE_CACHE.pop(
        workspace_id,
        None,
    )


def clear_public_profile_cache():
    _PROFILE_CACHE.clear()