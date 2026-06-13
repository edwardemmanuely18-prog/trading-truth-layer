from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.trade import Trade
from app.models.evidence_record import EvidenceRecord
from app.models.import_provenance import ImportProvenance
from app.models.integrity_registry import IntegrityRegistry
from app.models.audit_event import AuditEvent

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