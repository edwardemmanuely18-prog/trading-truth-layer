from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.api.deps import (
    get_current_user,
    require_workspace_member,
)

from app.models.user import User
from app.models.import_batch import ImportBatch

router = APIRouter()


@router.get(
    "/workspaces/{workspace_id}/import-batches"
)
def get_import_batches(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    batches = (
        db.query(ImportBatch)
        .filter(
            ImportBatch.workspace_id
            == workspace_id
        )
        .order_by(
            ImportBatch.id.desc()
        )
        .all()
    )

    return [
        {
            "id": batch.id,
            "filename": batch.filename,
            "source_type": batch.source_type,
            "rows_received": batch.rows_received,
            "rows_imported": batch.rows_imported,
            "rows_rejected": batch.rows_rejected,
            "rows_skipped_duplicates":
                batch.rows_skipped_duplicates,
            "adapter_name":
                batch.adapter_name,
            "batch_hash":
                batch.batch_hash,
            "created_at":
                batch.created_at,
        }
        for batch in batches
    ]