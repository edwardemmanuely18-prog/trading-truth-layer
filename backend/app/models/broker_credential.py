from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
)
from sqlalchemy.sql import func

from app.core.db import Base


class BrokerCredential(Base):
    __tablename__ = "broker_credentials"

    id = Column(Integer, primary_key=True)

    connection_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    credential_type = Column(
        String,
        nullable=False,
    )

    username = Column(String)
    password_encrypted = Column(String)

    api_key_encrypted = Column(String)
    api_secret_encrypted = Column(String)

    server_name = Column(String)

    host = Column(String)

    port = Column(Integer)

    client_id = Column(Integer)

    account_id = Column(String)

    gateway_mode = Column(String)

    flex_enabled = Column(Boolean, default=False)

    flex_query_id = Column(String)

    flex_query_name = Column(String)

    flex_token_encrypted = Column(String)

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )