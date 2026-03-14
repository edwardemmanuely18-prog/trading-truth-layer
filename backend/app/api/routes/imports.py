from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.import_batch import ImportBatch

router = APIRouter()


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
            "rows_received": row.rows_received,
            "rows_imported": row.rows_imported,
            "rows_rejected": row.rows_rejected,
            "rows_skipped_duplicates": row.rows_skipped_duplicates,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]