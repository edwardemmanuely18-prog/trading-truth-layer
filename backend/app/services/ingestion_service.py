from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.import_batch import ImportBatch
from app.models.claim_schema import ClaimSchema
from app.services.adapters.csv_adapter import CSVTradeAdapter
from app.services.audit_service import log_audit_event
from app.services.trade_import import parse_rows_by_source, process_import_rows


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
                closed_at=row.closed_at,
                entry_price=row.entry_price,
                exit_price=row.exit_price,
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

def import_broker_trades(
    *,
    db: Session,
    workspace_id: int,
    filename: str,
    content: bytes,
    source_type: str,
    actor_user_id: int | None = None,
):
    normalized_source = (source_type or "csv").strip().lower()

    rows = parse_rows_by_source(normalized_source, content)
    result = process_import_rows(rows, source_type=normalized_source)

    rows_received = int(result["stats"]["received"] or 0)
    rows_imported = 0
    rows_rejected = 0
    rows_skipped_duplicates = int(result["stats"]["duplicates"] or 0)
    errors: list[str] = []

    normalized_preview = result.get("normalized", [])[:20]
    rejected_preview = list(result.get("rejected", []))
    duplicate_preview = list(result.get("duplicates", []))

    locked_trade_lookup = build_locked_trade_lookup(db, workspace_id)

    for idx, trade_row in enumerate(result["normalized"], start=1):
        try:
            from datetime import datetime

            timestamp_raw = trade_row.get("timestamp")
            opened_at = None

            if isinstance(timestamp_raw, datetime):
                opened_at = timestamp_raw
            elif isinstance(timestamp_raw, str) and timestamp_raw.strip():
                text = timestamp_raw.strip()
                for fmt in [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                    "%Y-%m-%dT%H:%M:%S",
                ]:
                    try:
                        opened_at = datetime.strptime(text, fmt)
                        break
                    except Exception:
                        pass

            if opened_at is None:
                rows_rejected += 1
                rejected_preview.append({
                    "row": trade_row,
                    "reason": "Invalid timestamp",
                })
                errors.append(f"Row {idx}: invalid timestamp")
                continue

            symbol = str(trade_row.get("symbol") or "").strip().upper()
            side = str(trade_row.get("side") or "").strip().upper()
            quantity = float(trade_row.get("quantity") or 0)
            price = float(trade_row.get("price") or 0)
            pnl = trade_row.get("pnl")
            pnl = float(pnl) if pnl is not None else None
            external_id = trade_row.get("external_id")

            # temporary safe defaults until richer account/member mapping is added
            member_id = 999
            currency = "USD"
            source_system = normalized_source.upper()

            fingerprint = build_trade_fingerprint(
                workspace_id=workspace_id,
                member_id=member_id,
                symbol=symbol,
                side=side,
                opened_at=opened_at,
                entry_price=price,
                quantity=quantity,
            )

            conflict = find_locked_claim_conflict_for_fingerprint(
                locked_trade_lookup=locked_trade_lookup,
                fingerprint=fingerprint,
            )
            if conflict:
                rows_rejected += 1
                rejected_preview.append({
                    "row": trade_row,
                    "reason": f"Conflicts with locked claim {conflict.id}",
                })
                errors.append(
                    f"Row {idx}: conflicts with locked claim {conflict.id} by exact locked trade match"
                )
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
                duplicate_preview.append({
                    "row": trade_row,
                    "reason": "Duplicate trade fingerprint",
                    "fingerprint": fingerprint,
                })
                continue

            trade = Trade(
                workspace_id=workspace_id,
                member_id=member_id,
                symbol=symbol,
                side=side,
                opened_at=opened_at,
                closed_at=None,
                entry_price=price,
                exit_price=None,
                quantity=quantity,
                net_pnl=pnl,
                currency=currency,
                strategy_tag=f"{normalized_source}_import",
                source_system=source_system,
                trade_fingerprint=fingerprint,
            )
            db.add(trade)
            rows_imported += 1

        except Exception as e:
            rows_rejected += 1
            rejected_preview.append({
                "row": trade_row,
                "reason": str(e),
            })
            errors.append(f"Row {idx}: {str(e)}")

    batch = ImportBatch(
        workspace_id=workspace_id,
        filename=filename,
        source_type=normalized_source,
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
            "format_type": normalized_source,
            "rows_received": rows_received,
            "rows_imported": rows_imported,
            "rows_rejected": rows_rejected,
            "rows_skipped_duplicates": rows_skipped_duplicates,
        },
        metadata={
            "source": "ingestion_service.import_broker_trades",
            "actor_user_id": actor_user_id,
            "error_count": len(errors),
        },
    )

    return {
        "workspace_id": workspace_id,
        "filename": filename,
        "format_type": normalized_source,
        "rows_received": rows_received,
        "rows_imported": rows_imported,
        "rows_rejected": rows_rejected,
        "rows_skipped_duplicates": rows_skipped_duplicates,
        "errors": errors[:20],
        "normalized_preview": normalized_preview[:20],
        "rejected_preview": rejected_preview[:20],
        "duplicate_preview": duplicate_preview[:20],
    }