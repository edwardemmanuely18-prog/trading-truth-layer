from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.audit_event import AuditEvent

router = APIRouter()


def serialize_audit_event(event: AuditEvent):
    return {
        "id": event.id,
        "event_type": event.event_type,
        "entity_type": event.entity_type,
        "entity_id": event.entity_id,
        "actor_id": event.actor_id,
        "workspace_id": event.workspace_id,
        "old_state": event.old_state,
        "new_state": event.new_state,
        "metadata_json": event.metadata_json,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


@router.get("/audit-events/latest")
def get_latest_audit_events(limit: int = 20, db: Session = Depends(get_db)):
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200

    events = (
        db.query(AuditEvent)
        .order_by(AuditEvent.id.desc())
        .limit(limit)
        .all()
    )

    return [serialize_audit_event(event) for event in events]


@router.get("/audit-events/entity/{entity_type}/{entity_id}")
def get_audit_events_for_entity(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.entity_type == entity_type,
            AuditEvent.entity_id == str(entity_id),
        )
        .order_by(AuditEvent.id.desc())
        .all()
    )

    return [serialize_audit_event(event) for event in events]


@router.get("/audit-events/workspace/{workspace_id}")
def get_audit_events_for_workspace(workspace_id: str, limit: int = 50, db: Session = Depends(get_db)):
    if limit < 1:
        limit = 1
    if limit > 500:
        limit = 500

    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.workspace_id == str(workspace_id))
        .order_by(AuditEvent.id.desc())
        .limit(limit)
        .all()
    )

    return [serialize_audit_event(event) for event in events]


@router.get("/audit-events/{audit_event_id}")
def get_audit_event_by_id(audit_event_id: int, db: Session = Depends(get_db)):
    event = db.query(AuditEvent).filter(AuditEvent.id == audit_event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Audit event not found")

    return serialize_audit_event(event)

@router.get("/workspaces/{workspace_id}/audit-events")
def get_workspace_audit_events_v2(
    workspace_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.workspace_id == str(workspace_id))
        .order_by(AuditEvent.id.desc())
        .limit(limit)
        .all()
    )

    return [serialize_audit_event(event) for event in events]  