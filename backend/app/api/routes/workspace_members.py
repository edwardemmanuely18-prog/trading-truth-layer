from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models import WorkspaceMembership, User

router = APIRouter()

@router.get("/workspace/{workspace_id}/members")
def get_workspace_members(workspace_id: int, db: Session = Depends(get_db)):
    members = (
        db.query(WorkspaceMembership, User)
        .join(User, WorkspaceMembership.user_id == User.id)
        .filter(WorkspaceMembership.workspace_id == workspace_id)
        .all()
    )

    return [
        {
            "id": m.WorkspaceMembership.id,
            "user_id": m.User.id,
            "email": m.User.email,
            "name": m.User.name,
            "role": m.WorkspaceMembership.role,
        }
        for m in members
    ]