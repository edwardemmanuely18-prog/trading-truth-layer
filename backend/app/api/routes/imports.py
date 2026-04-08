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

router = APIRouter()


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

    try:
        rows = parse_rows_by_source(normalized_source, file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse import file: {exc}") from exc

    result = process_import_rows(rows, source_type=normalized_source)

    batch = create_batch_record(
        db=db,
        workspace_id=workspace_id,
        filename=file.filename,
        source_type=normalized_source,
        rows_received=result["stats"]["received"],
        rows_imported=result["stats"]["accepted"],
        rows_rejected=result["stats"]["rejected"],
        rows_skipped_duplicates=result["stats"]["duplicates"],
        status="completed",
    )

    return {
        **serialize_import_batch(batch),
        "mode": mode,
        "normalized_preview": result["normalized"][:20],
        "rejected_preview": result["rejected"][:20],
        "duplicate_preview": result["duplicates"][:20],
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

    if source_type not in {"csv", "mt5", "ibkr"}:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {source_type}")

    if not isinstance(trade, dict):
        raise HTTPException(status_code=400, detail="Missing trade payload")

    event_payload = build_stream_event_payload(
        workspace_id=workspace_id,
        source_type=source_type,
        trade=trade,
    )

    return {
        "workspace_id": workspace_id,
        "source_type": source_type,
        "event": event_payload,
        "message": "Real-time ingestion event accepted (foundation only)",
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