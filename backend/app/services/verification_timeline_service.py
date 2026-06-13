from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


TIMELINE_EVENT_LABELS = {
    "claim_schema_created": "Created",
    "claim_schema_verified": "Verified",
    "claim_schema_published": "Published",
    "claim_schema_locked": "Locked",
    "claim_compromised": "Compromised",
    "claim_downloaded": "Downloaded",
    "claim_reviewed": "Reviewed",
    "claim_externally_verified": "Verified Externally",
}


def build_claim_timeline(
    db: Session,
    claim_id: int,
):
    events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.entity_type == "claim_schema",
            AuditEvent.entity_id == str(claim_id),
        )
        .order_by(
            AuditEvent.created_at.asc()
        )
        .all()
    )

    timeline = []

    for event in events:

        timeline.append(
            {
                "event_type": event.event_type,
                "label": TIMELINE_EVENT_LABELS.get(
                    event.event_type,
                    event.event_type,
                ),
                "created_at": (
                    event.created_at.isoformat()
                    if event.created_at
                    else None
                ),
                "actor_id": event.actor_id,
                "metadata": event.metadata_json,
            }
        )

    return {
        "claim_id": claim_id,
        "event_count": len(timeline),
        "timeline": timeline,
    }