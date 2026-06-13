from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.trade import Trade
from app.models.import_provenance import ImportProvenance
from app.models.integrity_registry import IntegrityRegistry
from app.models.audit_event import AuditEvent
from app.models.evidence_record import (
    EvidenceRecord,
)
from app.models.import_batch import (
    ImportBatch,
)
from app.models.ingestion_session import (
    IngestionSession,
)


router = APIRouter()


@router.get(
    "/workspaces/{workspace_id}/evidence-registry"
)
def get_evidence_registry(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    trade_count = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id
        )
        .count()
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

    integrity_count = (
        db.query(IntegrityRegistry)
        .filter(
            IntegrityRegistry.workspace_id == workspace_id
        )
        .count()
    )

    audit_count = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.workspace_id == str(workspace_id)
        )
        .count()
    )

    return {
        "workspace_id": workspace_id,

        "trade_ledger": {
            "trade_count": trade_count,
        },

        "evidence_registry": {
            "evidence_records": evidence_count,
        },

        "import_registry": {
            "import_batches": provenance_count,
        },

        "integrity_registry": {
            "integrity_records": integrity_count,
        },

        "audit_timeline": {
            "audit_events": audit_count,
        },
    }


@router.get(
    "/workspaces/{workspace_id}/evidence-registry/trades"
)
def get_trade_ledger(
    workspace_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    trades = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id
        )
        .order_by(
            Trade.id.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": t.id,
            "symbol": t.symbol,
            "side": t.side,
            "source_system": t.source_system,
            "trade_fingerprint": t.trade_fingerprint,
            "import_batch_id": t.import_batch_id,
            "ingestion_session_id":
                t.ingestion_session_id,
        }
        for t in trades
    ]


@router.get(
    "/workspaces/{workspace_id}/evidence-registry/evidence-records"
)
def get_evidence_records(
    workspace_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    records = (
        db.query(EvidenceRecord)
        .filter(
            EvidenceRecord.workspace_id == workspace_id
        )
        .order_by(
            EvidenceRecord.id.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "trade_id": r.trade_id,
            "evidence_type": r.evidence_type,
            "evidence_hash": r.evidence_hash,
            "created_at": r.created_at,
        }
        for r in records
    ]


@router.get(
    "/workspaces/{workspace_id}/evidence-registry/import-batches"
)
def get_import_batches(
    workspace_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    batches = (
        db.query(ImportBatch)
        .filter(
            ImportBatch.workspace_id == workspace_id
        )
        .order_by(
            ImportBatch.id.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": b.id,
            "filename": b.filename,
            "source_type": b.source_type,
            "rows_received": b.rows_received,
            "rows_imported": b.rows_imported,
            "created_at": b.created_at,
        }
        for b in batches
    ]


@router.get(
    "/workspaces/{workspace_id}/evidence-registry/ingestion-sessions"
)
def get_ingestion_sessions(
    workspace_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(IngestionSession)
        .filter(
            IngestionSession.workspace_id == workspace_id
        )
        .order_by(
            IngestionSession.id.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": s.id,
            "source_type": s.source_type,
            "source_name": s.source_name,
            "ingestion_mode": s.ingestion_mode,
            "session_status": s.session_status,
            "rows_imported": s.rows_imported,
            "created_at": s.created_at,
        }
        for s in sessions
    ]


@router.get(
    "/workspaces/{workspace_id}/evidence-registry/integrity"
)
def get_integrity_registry(
    workspace_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    records = (
        db.query(IntegrityRegistry)
        .filter(
            IntegrityRegistry.workspace_id == workspace_id
        )
        .order_by(
            IntegrityRegistry.id.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "trade_id": r.trade_id,
            "integrity_status":
                r.integrity_status,
            "integrity_hash":
                r.integrity_hash,
            "verification_source":
                r.verification_source,
        }
        for r in records
    ]


@router.get(
    "/workspaces/{workspace_id}/evidence-registry/audit-timeline"
)
def get_audit_timeline(
    workspace_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.workspace_id == str(
                workspace_id
            )
        )
        .order_by(
            AuditEvent.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "entity_type": e.entity_type,
            "entity_id": e.entity_id,
            "created_at": e.created_at,
        }
        for e in events
    ]


