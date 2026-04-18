from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.workspace_membership import WorkspaceMembership

router = APIRouter()

@router.get("/workspace/{workspace_id}/members")
def get_workspace_members(workspace_id: int, db: Session = Depends(get_db)):
    members = (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id)
        .all()
    )

    return [
        {
            "id": m.id,
            "user_id": m.user_id,
            "role": m.role,
        }
        for m in members
    ]