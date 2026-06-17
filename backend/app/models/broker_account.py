from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)

from app.core.db import Base


class BrokerAccount(Base):

    __tablename__ = "broker_accounts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    connection_id = Column(
        Integer,
        ForeignKey(
            "broker_connections.id"
        ),
        nullable=False,
        index=True,
    )

    broker_account_id = Column(
        String,
        nullable=False,
        index=True,
    )

    account_name = Column(
        String,
        nullable=True,
    )

    environment = Column(
        String,
        nullable=True,
    )

    currency = Column(
        String,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
        default="active",
    )