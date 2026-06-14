from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.core.db import Base


class BrokerConnection(Base):
    __tablename__ = "broker_connections"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    provider = Column(
        String,
        nullable=False,
        index=True,
    )

    connection_name = Column(
        String,
        nullable=False,
    )

    connection_status = Column(
        String,
        nullable=False,
        default="not_connected",
    )

    verification_status = Column(
        String,
        nullable=False,
        default="pending",
    )

    last_sync_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )