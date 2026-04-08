from datetime import datetime
from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.import_batch import ImportBatch
from app.models.claim_schema import ClaimSchema
from app.services.adapters.csv_adapter import CSVTradeAdapter
from app.services.audit_service import log_audit_event
from app.services.trade_import import (
    normalize_side,
    normalize_symbol,
    parse_rows_by_source,
    parse_datetime,
    process_import_rows,
    safe_float,
)


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


def build_runtime_trade_fingerprint(
    *,
    workspace_id: int,
    member_id: int,
    symbol: str,
    side: str,
    opened_at: datetime,
    entry_price: float,
    quantity: float,
) -> str:
    return build_trade_fingerprint(
        workspace_id=workspace_id,
        member_id=member_id,
        symbol=symbol,
        side=side,
        opened_at=opened_at,
        entry_price=entry_price,
        quantity=quantity,
    )


def coerce_runtime_trade_row(
    *,
    trade_row: dict,
    source_type: str,
    default_member_id: int = 999,
    default_currency: str = "USD",
) -> dict:
    normalized_source = (source_type or "csv").strip().lower()

    opened_at = trade_row.get("opened_at")
    if not isinstance(opened_at, datetime):
        opened_at = parse_datetime(opened_at)

    closed_at = trade_row.get("closed_at")
    if closed_at is not None and not isinstance(closed_at, datetime):
        closed_at = parse_datetime(closed_at)

    symbol = normalize_symbol(trade_row.get("symbol"))
    side = normalize_side(trade_row.get("side"))
    quantity = safe_float(trade_row.get("quantity"), 0.0)
    entry_price = safe_float(trade_row.get("entry_price"), 0.0)

    exit_price_raw = trade_row.get("exit_price")
    exit_price = safe_float(exit_price_raw, None) if exit_price_raw not in (None, "") else None

    net_pnl_raw = trade_row.get("net_pnl")
    net_pnl = safe_float(net_pnl_raw, None) if net_pnl_raw not in (None, "") else None

    member_id_raw = trade_row.get("member_id")
    try:
        member_id = int(member_id_raw) if member_id_raw not in (None, "") else default_member_id
    except Exception:
        member_id = default_member_id

    currency = str(trade_row.get("currency") or default_currency).strip().upper() or default_currency
    strategy_tag = (str(trade_row.get("strategy_tag") or "").strip() or None)
    source_system = (
        str(trade_row.get("source_system") or normalized_source.upper()).strip()
        or normalized_source.upper()
    )

    return {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "net_pnl": net_pnl,
        "opened_at": opened_at,
        "closed_at": closed_at,
        "member_id": member_id,
        "currency": currency,
        "strategy_tag": strategy_tag,
        "source_system": source_system,
        "source_type": normalized_source,
        "external_id": trade_row.get("external_id"),
    }


def persist_runtime_trade_rows(
    *,
    db: Session,
    workspace_id: int,
    filename: str,
    source_type: str,
    normalized_rows: list[dict],
    actor_user_id: int | None = None,
    audit_source: str = "ingestion_service.persist_runtime_trade_rows",
):
    normalized_source = (source_type or "csv").strip().lower()

    rows_received = len(normalized_rows)
    rows_imported = 0
    rows_rejected = 0
    rows_skipped_duplicates = 0
    errors: list[str] = []
    rejected_preview: list[dict] = []
    duplicate_preview: list[dict] = []
    accepted_preview: list[dict] = []

    locked_trade_lookup = build_locked_trade_lookup(db, workspace_id)
    seen_persisted_fingerprints: set[str] = set()

    for idx, trade_row in enumerate(normalized_rows, start=1):
        try:
            runtime_trade = coerce_runtime_trade_row(
                trade_row=trade_row,
                source_type=normalized_source,
            )

            opened_at = runtime_trade["opened_at"]
            if opened_at is None:
                rows_rejected += 1
                rejected_preview.append(
                    {
                        "row": trade_row,
                        "reason": "Invalid opened_at",
                    }
                )
                errors.append(f"Row {idx}: invalid opened_at")
                continue

            if not runtime_trade["symbol"]:
                rows_rejected += 1
                rejected_preview.append(
                    {
                        "row": trade_row,
                        "reason": "Missing symbol",
                    }
                )
                errors.append(f"Row {idx}: missing symbol")
                continue

            if runtime_trade["side"] == "unknown":
                rows_rejected += 1
                rejected_preview.append(
                    {
                        "row": trade_row,
                        "reason": "Invalid side",
                    }
                )
                errors.append(f"Row {idx}: invalid side")
                continue

            if runtime_trade["quantity"] <= 0:
                rows_rejected += 1
                rejected_preview.append(
                    {
                        "row": trade_row,
                        "reason": "Invalid quantity",
                    }
                )
                errors.append(f"Row {idx}: invalid quantity")
                continue

            if runtime_trade["entry_price"] <= 0:
                rows_rejected += 1
                rejected_preview.append(
                    {
                        "row": trade_row,
                        "reason": "Invalid entry_price",
                    }
                )
                errors.append(f"Row {idx}: invalid entry_price")
                continue

            fingerprint = build_runtime_trade_fingerprint(
                workspace_id=workspace_id,
                member_id=runtime_trade["member_id"],
                symbol=runtime_trade["symbol"],
                side=runtime_trade["side"],
                opened_at=runtime_trade["opened_at"],
                entry_price=runtime_trade["entry_price"],
                quantity=runtime_trade["quantity"],
            )

            conflict = find_locked_claim_conflict_for_fingerprint(
                locked_trade_lookup=locked_trade_lookup,
                fingerprint=fingerprint,
            )
            if conflict:
                rows_rejected += 1
                rejected_preview.append(
                    {
                        "row": trade_row,
                        "reason": f"Conflicts with locked claim {conflict.id}",
                    }
                )
                errors.append(
                    f"Row {idx}: conflicts with locked claim {conflict.id} by exact locked trade match"
                )
                continue

            if fingerprint in seen_persisted_fingerprints:
                rows_skipped_duplicates += 1
                duplicate_preview.append(
                    {
                        "row": trade_row,
                        "reason": "Duplicate trade fingerprint",
                        "fingerprint": fingerprint,
                    }
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
                duplicate_preview.append(
                    {
                        "row": trade_row,
                        "reason": "Duplicate trade fingerprint",
                        "fingerprint": fingerprint,
                    }
                )
                continue

            trade = Trade(
                workspace_id=workspace_id,
                member_id=runtime_trade["member_id"],
                symbol=runtime_trade["symbol"],
                side=runtime_trade["side"].upper(),
                opened_at=runtime_trade["opened_at"],
                closed_at=runtime_trade["closed_at"],
                entry_price=runtime_trade["entry_price"],
                exit_price=runtime_trade["exit_price"],
                quantity=runtime_trade["quantity"],
                net_pnl=runtime_trade["net_pnl"],
                currency=runtime_trade["currency"],
                strategy_tag=runtime_trade["strategy_tag"],
                source_system=runtime_trade["source_system"],
                trade_fingerprint=fingerprint,
            )
            db.add(trade)
            rows_imported += 1
            seen_persisted_fingerprints.add(fingerprint)

            accepted_preview.append(
                {
                    **runtime_trade,
                    "fingerprint": fingerprint,
                }
            )

        except Exception as e:
            rows_rejected += 1
            rejected_preview.append(
                {
                    "row": trade_row,
                    "reason": str(e),
                }
            )
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
            "source": audit_source,
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
        "normalized_preview": accepted_preview[:20],
        "rejected_preview": rejected_preview[:20],
        "duplicate_preview": duplicate_preview[:20],
        "import_batch_id": batch.id,
    }


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

    persisted = persist_runtime_trade_rows(
        db=db,
        workspace_id=workspace_id,
        filename=filename,
        source_type=normalized_source,
        normalized_rows=result.get("normalized", []),
        actor_user_id=actor_user_id,
        audit_source="ingestion_service.import_broker_trades",
    )

    persisted["rows_received"] = int(result["stats"]["received"] or 0)
    persisted["rows_rejected"] = int(result["stats"]["rejected"] or 0) + int(
        persisted["rows_rejected"] or 0
    )
    persisted["rows_skipped_duplicates"] = int(result["stats"]["duplicates"] or 0) + int(
        persisted["rows_skipped_duplicates"] or 0
    )

    normalization_rejections = list(result.get("rejected", []))
    normalization_duplicates = list(result.get("duplicates", []))

    persisted["rejected_preview"] = (
        normalization_rejections + list(persisted.get("rejected_preview", []))
    )[:20]
    persisted["duplicate_preview"] = (
        normalization_duplicates + list(persisted.get("duplicate_preview", []))
    )[:20]

    return persisted