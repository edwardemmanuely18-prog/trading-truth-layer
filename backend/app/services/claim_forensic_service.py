from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.evidence_record import EvidenceRecord
from app.models.import_provenance import ImportProvenance
from app.models.integrity_registry import IntegrityRegistry


def validate_trade_forensics(
    db: Session,
    *,
    workspace_id: int,
    trade: Trade,
):
    evidence_exists = (
        db.query(EvidenceRecord)
        .filter(
            EvidenceRecord.workspace_id == workspace_id,
            EvidenceRecord.trade_id == trade.id,
        )
        .first()
    )

    provenance_exists = (
        db.query(ImportProvenance)
        .filter(
            ImportProvenance.workspace_id == workspace_id,
        )
        .first()
    )

    integrity_exists = (
        db.query(IntegrityRegistry)
        .filter(
            IntegrityRegistry.workspace_id == workspace_id,
            IntegrityRegistry.trade_id == trade.id,
        )
        .first()
    )

    return {
        "trade_id": trade.id,
        "evidence_exists": evidence_exists is not None,
        "provenance_exists": provenance_exists is not None,
        "integrity_exists": integrity_exists is not None,
        "forensically_verified": (
            evidence_exists is not None
            and provenance_exists is not None
            and integrity_exists is not None
        ),
    }


def validate_claim_forensics(
    db: Session,
    *,
    workspace_id: int,
    trades: list[Trade],
):
    trade_results = []

    for trade in trades:

        result = validate_trade_forensics(
            db=db,
            workspace_id=workspace_id,
            trade=trade,
        )

        trade_results.append(result)

    verified_count = sum(
        1
        for x in trade_results
        if x["forensically_verified"]
    )

    total_count = len(trade_results)

    return {
        "total_trades": total_count,
        "verified_trades": verified_count,
        "missing_trades": total_count - verified_count,
        "forensic_coverage": (
            verified_count / total_count
            if total_count
            else 0.0
        ),
        "fully_verified": (
            verified_count == total_count
        ),
        "trade_results": trade_results,
    }