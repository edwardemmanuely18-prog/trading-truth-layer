from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
)
from datetime import datetime

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
    )

    role = Column(
        String,
        default="member",
    )

    password_hash = Column(
        String,
        nullable=True,
    )

    email_verified = Column(
        Boolean,
        default=False,
    )

    email_verification_token = Column(
        String,
        nullable=True,
    )

    email_verification_expires_at = Column(
        DateTime,
        nullable=True,
    )

    password_reset_token = Column(
        String,
        nullable=True,
    )

    password_reset_expires_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )