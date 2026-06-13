from sqlalchemy.orm import Session

from app.models.trade import Trade

from app.services.evidence_service import (
    create_evidence_record,
)

from app.services.provenance_service import (
    create_import_provenance,
)

from app.services.integrity_service import (
    create_integrity_registry_entry,
)

from app.services.audit_service import (
    log_audit_event,
)


def register_trade_forensics(
    db: Session,
    *,
    workspace_id: int,
    trade: Trade,
    import_batch_id: int | None,
    ingestion_session_id: int | None,
    preview_session_id: int | None = None,
):
    provenance = create_import_provenance(
        db=db,
        workspace_id=workspace_id,
        preview_session_id=preview_session_id,
        ingestion_session_id=ingestion_session_id,
        import_batch_id=import_batch_id,
        trade_fingerprint=trade.trade_fingerprint,
    )

    evidence_payload = {
        "workspace_id": workspace_id,
        "trade_id": trade.id,
        "member_id": trade.member_id,
        "symbol": trade.symbol,
        "side": trade.side,
        "quantity": trade.quantity,
        "entry_price": trade.entry_price,
        "exit_price": trade.exit_price,
        "currency": trade.currency,
        "strategy_tag": trade.strategy_tag,
        "opened_at": trade.opened_at,
        "closed_at": trade.closed_at,
        "source_system": trade.source_system,
        "trade_fingerprint": trade.trade_fingerprint,
        "import_batch_id": import_batch_id,
        "provenance_hash": provenance.provenance_hash,
    }

    evidence_record = create_evidence_record(
        db=db,
        workspace_id=workspace_id,
        trade_id=trade.id,
        import_batch_id=import_batch_id,
        ingestion_session_id=ingestion_session_id,
        payload=evidence_payload,
    )

    create_integrity_registry_entry(
        db=db,
        workspace_id=workspace_id,
        trade_id=trade.id,
        trade_fingerprint=trade.trade_fingerprint,
        evidence_record_id=evidence_record.id,
        evidence_hash=evidence_record.evidence_hash,
        verification_source="trade_import",
    )

    log_audit_event(
        db,
        event_type="trade_evidence_registered",
        entity_type="trade",
        entity_id=trade.id,
        workspace_id=workspace_id,
        old_state=None,
        new_state={
            "trade_id": trade.id,
            "trade_fingerprint": trade.trade_fingerprint,
            "evidence_hash": evidence_record.evidence_hash,
            "provenance_hash": provenance.provenance_hash,
        },
    )

    return {
        "evidence_hash": evidence_record.evidence_hash,
        "provenance_hash": provenance.provenance_hash,
    }