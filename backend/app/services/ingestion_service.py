from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.import_batch import ImportBatch
from app.models.claim_schema import ClaimSchema
from app.services.adapters.base import NormalizedTradeRow
from app.services.adapters.csv_adapter import CSVTradeAdapter
from app.services.audit_service import log_audit_event


def build_trade_fingerprint(
    workspace_id: int,
    member_id: int,
    symbol: str,
    side: str,
    opened_at,
    entry_price: float,
    quantity: float,
) -> str:
    import hashlib

    raw = "|".join(
        [
            str(workspace_id),
            str(member_id),
            symbol.strip().upper(),
            side.strip().upper(),
            opened_at.isoformat(),
            f"{entry_price:.8f}",
            f"{quantity:.8f}",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_trade_fingerprint_from_trade(trade: Trade) -> str:
    if trade.trade_fingerprint:
        return trade.trade_fingerprint

    return build_trade_fingerprint(
        workspace_id=trade.workspace_id,
        member_id=trade.member_id,
        symbol=trade.symbol,
        side=trade.side,
        opened_at=trade.opened_at,
        entry_price=trade.entry_price,
        quantity=trade.quantity,
    )


def get_locked_claims(db: Session, workspace_id: int) -> list[ClaimSchema]:
    return (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status == "locked",
        )
        .all()
    )


def build_locked_trade_lookup(db: Session, workspace_id: int) -> dict[str, ClaimSchema]:
    import json

    locked_claims = get_locked_claims(db, workspace_id)
    locked_trade_ids: set[int] = set()

    for claim in locked_claims:
        claim_trade_ids = json.loads(claim.locked_trade_ids_json or "[]")
        for trade_id in claim_trade_ids:
            try:
                locked_trade_ids.add(int(trade_id))
            except Exception:
                continue

    if not locked_trade_ids:
        return {}

    locked_trades = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id,
            Trade.id.in_(locked_trade_ids),
        )
        .all()
    )

    trade_by_id = {trade.id: trade for trade in locked_trades}
    fingerprint_to_claim: dict[str, ClaimSchema] = {}

    for claim in locked_claims:
        claim_trade_ids = json.loads(claim.locked_trade_ids_json or "[]")
        for raw_trade_id in claim_trade_ids:
            try:
                trade_id = int(raw_trade_id)
            except Exception:
                continue

            trade = trade_by_id.get(trade_id)
            if not trade:
                continue

            fingerprint = build_trade_fingerprint_from_trade(trade)
            if fingerprint not in fingerprint_to_claim:
                fingerprint_to_claim[fingerprint] = claim

    return fingerprint_to_claim


def find_locked_claim_conflict_for_fingerprint(
    locked_trade_lookup: dict[str, ClaimSchema],
    fingerprint: str,
) -> ClaimSchema | None:
    return locked_trade_lookup.get(fingerprint)


def import_csv_trades(
    *,
    db: Session,
    workspace_id: int,
    filename: str,
    content: bytes,
    actor_user_id: int | None = None,
):
    adapter = CSVTradeAdapter()
    normalized_rows, format_type = adapter.parse(content)

    rows_received = len(normalized_rows)
    rows_imported = 0
    rows_rejected = 0
    rows_skipped_duplicates = 0
    errors: list[str] = []

    locked_trade_lookup = build_locked_trade_lookup(db, workspace_id)

    # Prevent duplicate inserts within the same uploaded file before commit.
    seen_in_file: set[str] = set()

    for idx, row in enumerate(normalized_rows, start=1):
        try:
            fingerprint = build_trade_fingerprint(
                workspace_id=workspace_id,
                member_id=row.member_id,
                symbol=row.symbol,
                side=row.side,
                opened_at=row.opened_at,
                entry_price=row.entry_price,
                quantity=row.quantity,
            )

            conflict = find_locked_claim_conflict_for_fingerprint(
                locked_trade_lookup=locked_trade_lookup,
                fingerprint=fingerprint,
            )
            if conflict:
                rows_rejected += 1
                errors.append(
                    f"Row {idx}: conflicts with locked claim {conflict.id} by exact locked trade match"
                )
                continue

            if fingerprint in seen_in_file:
                rows_skipped_duplicates += 1
                continue

            existing = (
                db.query(Trade)
                .filter(
                    Trade.workspace_id == workspace_id,
                    Trade.trade_fingerprint == fingerprint,
                )
                .first()
            )

            if existing:
                rows_skipped_duplicates += 1
                seen_in_file.add(fingerprint)
                continue

            trade = Trade(
                workspace_id=workspace_id,
                member_id=row.member_id,
                symbol=row.symbol,
                side=row.side,
                opened_at=row.opened_at,
                closed_at=None,
                entry_price=row.entry_price,
                exit_price=None,
                quantity=row.quantity,
                net_pnl=row.net_pnl,
                currency=row.currency,
                strategy_tag=row.strategy_tag,
                source_system=row.source_system,
                trade_fingerprint=fingerprint,
            )
            db.add(trade)
            rows_imported += 1
            seen_in_file.add(fingerprint)

        except Exception as e:
            rows_rejected += 1
            errors.append(f"Row {idx}: {str(e)}")

    batch = ImportBatch(
        workspace_id=workspace_id,
        filename=filename,
        source_type=format_type,
        rows_received=rows_received,
        rows_imported=rows_imported,
        rows_rejected=rows_rejected,
        rows_skipped_duplicates=rows_skipped_duplicates,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    log_audit_event(
        db,
        event_type="trade_import_completed",
        entity_type="import_batch",
        entity_id=batch.id,
        workspace_id=workspace_id,
        old_state=None,
        new_state={
            "import_batch_id": batch.id,
            "filename": filename,
            "format_type": format_type,
            "rows_received": rows_received,
            "rows_imported": rows_imported,
            "rows_rejected": rows_rejected,
            "rows_skipped_duplicates": rows_skipped_duplicates,
        },
        metadata={
            "source": "ingestion_service.import_csv_trades",
            "actor_user_id": actor_user_id,
            "error_count": len(errors),
        },
    )

    return {
        "workspace_id": workspace_id,
        "filename": filename,
        "format_type": format_type,
        "rows_received": rows_received,
        "rows_imported": rows_imported,
        "rows_rejected": rows_rejected,
        "rows_skipped_duplicates": rows_skipped_duplicates,
        "errors": errors[:20],
    }