from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)

    role = Column(String, default="member")

    created_at = Column(DateTime, default=datetime.utcnow)