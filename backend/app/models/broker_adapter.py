from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.core.db import Base


class BrokerAdapter(Base):
    __tablename__ = "broker_adapters"

    id = Column(Integer, primary_key=True, index=True)

    provider = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    display_name = Column(
        String,
        nullable=False,
    )

    adapter_type = Column(
        String,
        nullable=False,
        default="broker_api",
    )

    trust_tier = Column(
        String,
        nullable=False,
        default="tier_1",
    )

    supports_live_sync = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    supports_historical_import = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    status = Column(
        String,
        nullable=False,
        default="active",
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