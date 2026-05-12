from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class WorkspaceInviteCreate(BaseModel):
    email: EmailStr
    role: str = "member"


class WorkspaceInviteResponse(BaseModel):
    id: int
    workspace_id: int
    email: str
    role: str

    status: str

    invited_by_user_id: Optional[int] = None
    accepted_by_user_id: Optional[int] = None

    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AcceptInviteResponse(BaseModel):
    message: str
    workspace_id: int
    role: str