from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.db import Base


class WorkspaceInvite(Base):
    __tablename__ = "workspace_invites"

    id = Column(Integer, primary_key=True, index=True)

    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False, default="member", index=True)

    token = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending", index=True)

    invited_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    accepted_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=7), nullable=False)
    accepted_at = Column(DateTime, nullable=True)