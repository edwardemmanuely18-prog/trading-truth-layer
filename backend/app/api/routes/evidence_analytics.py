from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.services.evidence_analytics_service import (
    build_evidence_analytics,
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
    return build_evidence_analytics(
        db,
        workspace_id,
    )