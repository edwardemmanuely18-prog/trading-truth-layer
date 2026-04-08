from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.import_batch import ImportBatch
from app.services.trade_import import (
    build_import_job_payload,
    build_stream_event_payload,
    parse_rows_by_source,
    process_import_rows,
)
from app.services.ingestion_service import (
    import_broker_trades,
    import_csv_trades,
    persist_runtime_trade_rows,
)

router = APIRouter()

WEBHOOK_ALLOWED_SOURCES = {"csv", "mt5", "ibkr", "custom", "webhook"}


def _normalize_webhook_source(source_type: str | None) -> str:
    normalized = str(source_type or "webhook").strip().lower()
    if normalized == "custom":
        return "webhook"
    return normalized


def _adapt_webhook_trade(raw_trade: dict, source_type: str) -> dict:
    return {
        "symbol": raw_trade.get("symbol") or raw_trade.get("ticker") or raw_trade.get("instrument"),
        "side": raw_trade.get("side") or raw_trade.get("action") or raw_trade.get("type"),
        "quantity": raw_trade.get("quantity") or raw_trade.get("qty") or raw_trade.get("size"),
        "entry_price": raw_trade.get("entry_price") or raw_trade.get("price") or raw_trade.get("fill_price"),
        "exit_price": raw_trade.get("exit_price"),
        "net_pnl": raw_trade.get("net_pnl") or raw_trade.get("pnl") or raw_trade.get("profit"),
        "opened_at": raw_trade.get("opened_at") or raw_trade.get("timestamp") or raw_trade.get("time"),
        "closed_at": raw_trade.get("closed_at"),
        "member_id": raw_trade.get("member_id"),
        "currency": raw_trade.get("currency"),
        "strategy_tag": raw_trade.get("strategy_tag"),
        "source_system": raw_trade.get("source_system") or source_type.upper(),
        "external_id": raw_trade.get("external_id") or raw_trade.get("id") or raw_trade.get("trade_id"),
    }


def _extract_webhook_trade_rows(payload: dict) -> list[dict]:
    trades = payload.get("trades")

    if isinstance(trades, list):
        return trades

    trade = payload.get("trade")
    if isinstance(trade, dict):
        return [trade]

    return []


# -----------------------------
# HELPERS
# -----------------------------
def serialize_import_batch(row: ImportBatch) -> Dict[str, Any]:
    return {
        "id": row.id,
        "workspace_id": row.workspace_id,
        "filename": row.filename,
        "source_type": row.source_type,
        "status": getattr(row, "status", "completed"),
        "rows_received": row.rows_received,
        "rows_imported": row.rows_imported,
        "rows_rejected": row.rows_rejected,
        "rows_skipped_duplicates": row.rows_skipped_duplicates,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def create_batch_record(
    *,
    db: Session,
    workspace_id: int,
    filename: str,
    source_type: str,
    rows_received: int,
    rows_imported: int,
    rows_rejected: int,
    rows_skipped_duplicates: int,
    status: str,
) -> ImportBatch:
    batch = ImportBatch(
        workspace_id=workspace_id,
        filename=filename,
        source_type=source_type,
        rows_received=rows_received,
        rows_imported=rows_imported,
        rows_rejected=rows_rejected,
        rows_skipped_duplicates=rows_skipped_duplicates,
        created_at=datetime.utcnow(),
    )

    if hasattr(batch, "status"):
        batch.status = status

    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


# -----------------------------
# LIST IMPORT BATCHES
# -----------------------------
@router.get("/workspaces/{workspace_id}/imports")
def list_import_batches(workspace_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(ImportBatch)
        .filter(ImportBatch.workspace_id == workspace_id)
        .order_by(ImportBatch.id.desc())
        .all()
    )

    return [serialize_import_batch(row) for row in rows]


# -----------------------------
# CREATE IMPORT BATCH (ENTRY POINT)
# -----------------------------
@router.post("/workspaces/{workspace_id}/imports")
def create_import_batch(
    workspace_id: int,
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    Canonical ingestion entry point.
    All source types should eventually route through this import control layer.
    """

    filename = payload.get("filename", "manual_import")
    source_type = payload.get("source_type", "manual")

    batch = create_batch_record(
        db=db,
        workspace_id=workspace_id,
        filename=filename,
        source_type=source_type,
        rows_received=payload.get("rows_received", 0),
        rows_imported=0,
        rows_rejected=0,
        rows_skipped_duplicates=0,
        status="processing",
    )

    return {
        "id": batch.id,
        "status": getattr(batch, "status", "processing"),
        "message": "Import batch created",
    }


# -----------------------------
# WEBHOOK INGESTION
# -----------------------------
@router.post("/webhooks/trades")
def ingest_webhook_trades(
    payload: dict,
    db: Session = Depends(get_db),
):
    workspace_id_raw = payload.get("workspace_id")
    try:
        workspace_id = int(workspace_id_raw)
    except Exception:
        raise HTTPException(status_code=400, detail="Missing or invalid workspace_id")

    source_type = _normalize_webhook_source(payload.get("source_type"))

    if source_type not in WEBHOOK_ALLOWED_SOURCES:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {source_type}")

    raw_trades = _extract_webhook_trade_rows(payload)
    if not raw_trades:
        raise HTTPException(status_code=400, detail="Missing trade payload")

    adapted_rows = [
        _adapt_webhook_trade(raw_trade, source_type)
        for raw_trade in raw_trades
        if isinstance(raw_trade, dict)
    ]

    if not adapted_rows:
        raise HTTPException(status_code=400, detail="No valid trade objects supplied")

    filename = str(payload.get("filename") or f"{source_type}_webhook")

    result = persist_runtime_trade_rows(
        db=db,
        workspace_id=workspace_id,
        filename=filename,
        source_type=source_type,
        normalized_rows=adapted_rows,
        actor_user_id=None,
        audit_source="imports.ingest_webhook_trades",
    )

    return {
        **result,
        "message": "Webhook trades ingested",
    }


# -----------------------------
# GENERIC FILE INGESTION
# -----------------------------
@router.post("/workspaces/{workspace_id}/imports/upload")
async def upload_import_file(
    workspace_id: int,
    file: UploadFile = File(...),
    source_type: str = Form("csv"),
    mode: str = Form("manual"),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    allowed_sources = {"csv", "mt5", "ibkr"}
    normalized_source = str(source_type or "").strip().lower()

    if normalized_source not in allowed_sources:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source type: {source_type}",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV-like file uploads are supported at this stage",
        )

    file_bytes = await file.read()

    # Persist accepted rows into Trade via existing ingestion service
    result = import_broker_trades(
        db=db,
        workspace_id=workspace_id,
        filename=file.filename,
        content=file_bytes,
        source_type=normalized_source,
        actor_user_id=None,
    )

    return {
        **result,
        "mode": mode,
        "job_payload": build_import_job_payload(
            workspace_id=workspace_id,
            source_type=normalized_source,
            filename=file.filename,
            mode=mode,
        ),
        "message": f"{normalized_source.upper()} import processed",
    }


# -----------------------------
# CSV INGESTION (BACKWARD COMPAT)
# -----------------------------
@router.post("/workspaces/{workspace_id}/imports/csv")
async def upload_csv_import(
    workspace_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_bytes = await file.read()
    rows = parse_rows_by_source("csv", file_bytes)
    result = process_import_rows(rows, source_type="csv")

    batch = create_batch_record(
        db=db,
        workspace_id=workspace_id,
        filename=file.filename,
        source_type="csv",
        rows_received=result["stats"]["received"],
        rows_imported=result["stats"]["accepted"],
        rows_rejected=result["stats"]["rejected"],
        rows_skipped_duplicates=result["stats"]["duplicates"],
        status="completed",
    )

    return {
        **serialize_import_batch(batch),
        "normalized_preview": result["normalized"][:20],
        "rejected_preview": result["rejected"][:20],
        "duplicate_preview": result["duplicates"][:20],
        "job_payload": build_import_job_payload(
            workspace_id=workspace_id,
            source_type="csv",
            filename=file.filename,
            mode="manual",
        ),
        "message": "CSV import processed",
    }


# -----------------------------
# AUTO-IMPORT FOUNDATION
# -----------------------------
@router.post("/workspaces/{workspace_id}/imports/auto")
def configure_auto_import(
    workspace_id: int,
    payload: dict,
):
    source_type = str(payload.get("source_type", "csv")).strip().lower()
    enabled = bool(payload.get("enabled", True))
    cadence = str(payload.get("cadence", "hourly")).strip().lower()

    if source_type not in {"csv", "mt5", "ibkr"}:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {source_type}")

    return {
        "workspace_id": workspace_id,
        "source_type": source_type,
        "enabled": enabled,
        "cadence": cadence,
        "job_payload": build_import_job_payload(
            workspace_id=workspace_id,
            source_type=source_type,
            filename=payload.get("filename"),
            mode="auto",
        ),
        "message": "Auto-import configuration captured (foundation only)",
    }


# -----------------------------
# REAL-TIME INGESTION FOUNDATION
# -----------------------------
@router.post("/workspaces/{workspace_id}/imports/stream-event")
def ingest_stream_event(
    workspace_id: int,
    payload: dict,
):
    source_type = str(payload.get("source_type", "ibkr")).strip().lower()
    trade = payload.get("trade")

@router.post("/workspaces/{workspace_id}/imports/stream-event")
def ingest_stream_event(
    workspace_id: int,
    payload: dict,
    db: Session = Depends(get_db),
):
    source_type = _normalize_webhook_source(payload.get("source_type", "ibkr"))
    trade = payload.get("trade")

    if source_type not in WEBHOOK_ALLOWED_SOURCES:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {source_type}")

    if not isinstance(trade, dict):
        raise HTTPException(status_code=400, detail="Missing trade payload")

    adapted_trade = _adapt_webhook_trade(trade, source_type)
    event_payload = build_stream_event_payload(
        workspace_id=workspace_id,
        source_type=source_type,
        trade=adapted_trade,
    )

    result = persist_runtime_trade_rows(
        db=db,
        workspace_id=workspace_id,
        filename=f"{source_type}_stream_event",
        source_type=source_type,
        normalized_rows=[adapted_trade],
        actor_user_id=None,
        audit_source="imports.ingest_stream_event",
    )

    return {
        **result,
        "workspace_id": workspace_id,
        "source_type": source_type,
        "event": event_payload,
        "message": "Real-time ingestion event processed",
    }


# -----------------------------
# GET SINGLE IMPORT BATCH
# -----------------------------
@router.get("/imports/{import_id}")
def get_import_batch(import_id: int, db: Session = Depends(get_db)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == import_id).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    return serialize_import_batch(batch)