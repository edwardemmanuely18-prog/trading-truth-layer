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


def parse_claim_period_start(date_str: str | None):
    from datetime import datetime

    if not date_str:
        return None
    return datetime.fromisoformat(date_str)


def parse_claim_period_end(date_str: str | None):
    from datetime import datetime, timedelta

    if not date_str:
        return None
    return datetime.fromisoformat(date_str) + timedelta(days=1)


def trade_matches_locked_claim(claim: ClaimSchema, row: NormalizedTradeRow) -> bool:
    import json

    included_members = json.loads(claim.included_member_ids_json or "[]")
    included_symbols = [s.upper() for s in json.loads(claim.included_symbols_json or "[]")]

    period_start = parse_claim_period_start(claim.period_start)
    period_end = parse_claim_period_end(claim.period_end)

    if period_start is not None and row.opened_at < period_start:
        return False

    if period_end is not None and row.opened_at >= period_end:
        return False

    if included_members and row.member_id not in included_members:
        return False

    if included_symbols and row.symbol.upper() not in included_symbols:
        return False

    return True


def find_locked_claim_conflict(db: Session, workspace_id: int, row: NormalizedTradeRow):
    locked_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status == "locked",
        )
        .all()
    )

    for claim in locked_claims:
        if trade_matches_locked_claim(claim, row):
            return claim

    return None


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

    for idx, row in enumerate(normalized_rows, start=1):
        try:
            conflict = find_locked_claim_conflict(db, workspace_id, row)
            if conflict:
                rows_rejected += 1
                errors.append(f"Row {idx}: conflicts with locked claim {conflict.id}")
                continue

            fingerprint = build_trade_fingerprint(
                workspace_id=workspace_id,
                member_id=row.member_id,
                symbol=row.symbol,
                side=row.side,
                opened_at=row.opened_at,
                entry_price=row.entry_price,
                quantity=row.quantity,
            )

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