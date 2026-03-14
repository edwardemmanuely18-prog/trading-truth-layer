from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditEventBase(BaseModel):
    event_type: str
    entity_type: str
    entity_id: str
    actor_id: Optional[str] = None
    workspace_id: Optional[str] = None
    old_state: Optional[str] = None
    new_state: Optional[str] = None
    metadata_json: Optional[str] = None


class AuditEventCreate(AuditEventBase):
    pass


class AuditEventRead(AuditEventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True