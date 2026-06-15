from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BrokerConnectionCreate(BaseModel):
    provider: str
    connection_name: str

    account_id: Optional[str] = None
    account_name: Optional[str] = None

    adapter_type: str = "broker_api"

    sync_mode: str = "manual"

    trust_tier: str = "tier_1"


class BrokerConnectionUpdate(BaseModel):
    connection_name: Optional[str] = None

    connection_status: Optional[str] = None

    sync_status: Optional[str] = None

    verification_status: Optional[str] = None

    last_sync_error: Optional[str] = None


class BrokerConnectionResponse(BaseModel):
    id: int

    workspace_id: int

    provider: str

    connection_name: str

    account_id: Optional[str]

    account_name: Optional[str]

    adapter_type: str

    sync_mode: str

    connection_status: str

    sync_status: str

    verification_status: str

    trust_tier: str

    last_sync_error: Optional[str]

    last_sync_at: Optional[datetime]

    verified_at: Optional[datetime]

    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True