import json
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


def _safe_json(value: Optional[Any]) -> Optional[str]:
    if value is None:
        return None
    try:
        return json.dumps(value, default=str)
    except Exception:
        return str(value)


def log_audit_event(
    db: Session,
    *,
    event_type: str,
    entity_type: str,
    entity_id: str,
    actor_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    old_state: Optional[Any] = None,
    new_state: Optional[Any] = None,
    metadata: Optional[Any] = None,
) -> AuditEvent:
    event = AuditEvent(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=str(entity_id),
        actor_id=str(actor_id) if actor_id is not None else None,
        workspace_id=str(workspace_id) if workspace_id is not None else None,
        old_state=_safe_json(old_state),
        new_state=_safe_json(new_state),
        metadata_json=_safe_json(metadata),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event