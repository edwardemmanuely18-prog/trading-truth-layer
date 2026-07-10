from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import SessionLocal

from app.services.governance.workspace_governance_snapshot_service import (
    get_workspace_governance_snapshot,
)


router = APIRouter(
    tags=["Workspace Governance"],
)


# ==========================================================
# DATABASE
# ==========================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# ==========================================================
# GOVERNANCE SNAPSHOT
# ==========================================================

@router.get(
    "/workspaces/{workspace_id}/governance",
)
def workspace_governance_snapshot(

    workspace_id: int,

    db: Session = Depends(get_db),

):

    return get_workspace_governance_snapshot(

        db=db,

        workspace_id=workspace_id,

    )