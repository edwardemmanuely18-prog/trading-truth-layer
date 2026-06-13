from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema
from app.models.evidence_record import EvidenceRecord
from app.models.import_provenance import ImportProvenance
from app.models.audit_event import AuditEvent

from app.services.integrity_monitor_service import (
    scan_workspace_claims,
)


def build_executive_dashboard(
    db: Session,
    workspace_id: int,
):
    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .all()
    )

    evidence_count = (
        db.query(EvidenceRecord)
        .filter(
            EvidenceRecord.workspace_id == workspace_id
        )
        .count()
    )

    provenance_count = (
        db.query(ImportProvenance)
        .filter(
            ImportProvenance.workspace_id == workspace_id
        )
        .count()
    )

    published_claims = sum(
        1
        for c in claims
        if c.status == "published"
    )

    locked_claims = sum(
        1
        for c in claims
        if c.status == "locked"
    )

    compromised_claims = sum(
        1
        for c in claims
        if c.status == "compromised"
    )

    integrity_scan = (
        scan_workspace_claims(
            db=db,
            workspace_id=workspace_id,
        )
    )

    recent_events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.workspace_id == str(
                workspace_id
            )
        )
        .order_by(
            AuditEvent.created_at.desc()
        )
        .limit(20)
        .all()
    )

    return {
        "portfolio_overview": {
            "claims": len(claims),
            "published_claims":
                published_claims,
            "locked_claims":
                locked_claims,
            "compromised_claims":
                compromised_claims,
        },

        "evidence_overview": {
            "evidence_records":
                evidence_count,
            "provenance_records":
                provenance_count,
        },

        "trust_overview": {
            "integrity_health":
                (
                    100.0
                    if compromised_claims == 0
                    else max(
                        0.0,
                        (
                            (
                                len(claims)
                                - compromised_claims
                            )
                            / len(claims)
                        )
                        * 100
                    )
                )
                if claims
                else 100.0,
        },

        "integrity_scan":
            integrity_scan,

        "activity": [
            {
                "event_type":
                    e.event_type,
                "entity_type":
                    e.entity_type,
                "entity_id":
                    e.entity_id,
                "created_at":
                    e.created_at,
            }
            for e in recent_events
        ],
    }