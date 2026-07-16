from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.api.deps import get_current_user

from app.models.user import User

from app.api.authorization_deps import (
    require_workspace_context,
)

from app.services.authorization.engine.authorization_service import (
    AuthorizationService,
)

from app.services.authorization.registry.capability_catalog import (
    EVIDENCE_READ,
)

from app.services.entitlements import (
    enforce_workspace_page_access,
)

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
    current_user: User = Depends(get_current_user),
):
    context = require_workspace_context(
        "evidence_analytics",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        EVIDENCE_READ,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="evidence_analytics",
        action="access Evidence Analytics",
    )

    projection = get_workspace_evidence_projection(

        db=db,

        workspace_id=workspace_id,

    )

    return projection.analytics