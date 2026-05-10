from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.core.db import Base


class ImportPreviewSession(Base):
    __tablename__ = "import_preview_sessions"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(Integer, nullable=False, index=True)

    source_type = Column(String, nullable=False)

    filename = Column(String, nullable=False)

    preview_payload_json = Column(Text, nullable=False)

    status = Column(String, nullable=False, default="pending_confirmation")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )