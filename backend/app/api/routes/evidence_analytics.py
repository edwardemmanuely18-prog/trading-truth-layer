from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.services.evidence.evidence_service import (
    get_workspace_evidence_projection,
)

router = APIRouter(
    prefix="/evidence-analytics",
    tags=["evidence-analytics"],
)


@router.get(
    "/{workspace_id}"
)
def evidence_analytics(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    projection = get_workspace_evidence_projection(

        db=db,

        workspace_id=workspace_id,

    )

    return projection.analytics