from pydantic import BaseModel


class WorkspacePreferencesRead(BaseModel):

    workspace_id: int

    timezone: str

    language: str

    currency: str

    date_format: str

    auto_refresh: bool

    auto_save: bool

    class Config:
        from_attributes = True


class WorkspacePreferencesUpdate(BaseModel):

    timezone: str

    language: str

    currency: str

    date_format: str

    auto_refresh: bool

    auto_save: bool