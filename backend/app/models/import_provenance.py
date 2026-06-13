from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.sql import func

from app.core.db import Base


class ImportProvenance(Base):
    __tablename__ = "import_provenance"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    workspace_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    preview_session_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    ingestion_session_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    import_batch_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    provenance_hash = Column(
        String,
        nullable=True,
        index=True,
    )