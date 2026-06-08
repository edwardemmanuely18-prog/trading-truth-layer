import json

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


def log_security_event(
    db: Session,
    event_type: str,
    user_id: int | None = None,
    email: str | None = None,
    ip_address: str | None = None,
    metadata: dict | None = None,
):
    event = AuditEvent(
        event_type=event_type,
        entity_type="security",
        entity_id=str(user_id or 0),
        actor_id=str(user_id) if user_id else None,
        metadata_json=json.dumps(
            {
                "email": email,
                "ip_address": ip_address,
                **(metadata or {}),
            }
        ),
    )

    db.add(event)
    db.commit()