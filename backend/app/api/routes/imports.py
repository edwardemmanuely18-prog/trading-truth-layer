from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.import_batch import ImportBatch
from app.services.trade_import import parse_csv_rows, process_import_rows

router = APIRouter()


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

    return [
        {
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
        for row in rows
    ]


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

    batch = ImportBatch(
        workspace_id=workspace_id,
        filename=filename,
        source_type=source_type,
        rows_received=payload.get("rows_received", 0),
        rows_imported=0,
        rows_rejected=0,
        rows_skipped_duplicates=0,
        created_at=datetime.utcnow(),
    )

    if hasattr(batch, "status"):
        batch.status = "processing"

    db.add(batch)
    db.commit()
    db.refresh(batch)

    return {
        "id": batch.id,
        "status": getattr(batch, "status", "processing"),
        "message": "Import batch created",
    }


# -----------------------------
# CSV INGESTION
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
    rows = parse_csv_rows(file_bytes)
    result = process_import_rows(rows)

    batch = ImportBatch(
        workspace_id=workspace_id,
        filename=file.filename,
        source_type="csv",
        rows_received=result["stats"]["received"],
        rows_imported=result["stats"]["accepted"],
        rows_rejected=result["stats"]["rejected"],
        rows_skipped_duplicates=0,
        created_at=datetime.utcnow(),
    )

    if hasattr(batch, "status"):
        batch.status = "completed"

    db.add(batch)
    db.commit()
    db.refresh(batch)

    return {
        "id": batch.id,
        "workspace_id": workspace_id,
        "filename": file.filename,
        "source_type": "csv",
        "status": getattr(batch, "status", "completed"),
        "rows_received": batch.rows_received,
        "rows_imported": batch.rows_imported,
        "rows_rejected": batch.rows_rejected,
        "rows_skipped_duplicates": batch.rows_skipped_duplicates,
        "created_at": batch.created_at.isoformat() if batch.created_at else None,
        "normalized_preview": result["normalized"][:20],
        "rejected_preview": result["rejected"][:20],
        "message": "CSV import processed",
    }


# -----------------------------
# GET SINGLE IMPORT BATCH
# -----------------------------
@router.get("/imports/{import_id}")
def get_import_batch(import_id: int, db: Session = Depends(get_db)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == import_id).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    return {
        "id": batch.id,
        "workspace_id": batch.workspace_id,
        "filename": batch.filename,
        "source_type": batch.source_type,
        "status": getattr(batch, "status", "completed"),
        "rows_received": batch.rows_received,
        "rows_imported": batch.rows_imported,
        "rows_rejected": batch.rows_rejected,
        "rows_skipped_duplicates": batch.rows_skipped_duplicates,
        "created_at": batch.created_at.isoformat() if batch.created_at else None,
    }