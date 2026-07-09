from fastapi import APIRouter

from app.services.runtime.runtime_snapshot_service import (
    RuntimeSnapshotService,
)

router = APIRouter(
    prefix="/api/workspaces",
    tags=["Runtime Snapshot"],
)


@router.get(
    "/{workspace_id}/runtime-snapshot"
)
def workspace_runtime_snapshot(
    workspace_id: int,
):
    return RuntimeSnapshotService.get_snapshot(
        workspace_id
    )