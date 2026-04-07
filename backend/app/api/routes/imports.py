from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.db import get_db
from app.models.import_batch import ImportBatch

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
    This is the canonical ingestion entry point.

    All import sources (manual, CSV, MT5, IBKR)
    should eventually hit this endpoint.
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

    # optional future field
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