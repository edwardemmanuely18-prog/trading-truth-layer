from app.core.db import engine, Base
from app.models.audit_event import AuditEvent  # noqa: F401

Base.metadata.create_all(bind=engine)
print("AUDIT_EVENTS_TABLE_READY")