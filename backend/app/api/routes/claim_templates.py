from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.api.authorization_deps import (
    require_workspace_context,
)

from app.api.deps import (
    get_current_user,
)

from app.models.user import (
    User,
)

from app.services.authorization.engine.authorization_service import (
    AuthorizationService,
)

from app.services.authorization.registry.capability_catalog import (
    REPORT_READ,
)

from app.services.entitlements import (
    enforce_workspace_page_access,
)

from app.models.claim_schema_preset import (
    ClaimSchemaPreset,
)

router = APIRouter(
    prefix="/claim-templates",
    tags=["Claim Templates"],
)


class CreateTemplateRequest(BaseModel):

    workspace_id: int

    name: str

    description: str | None = None

    template_type: str = "custom"

    included_member_ids_json: list[int] = []

    included_symbols_json: list[str] = []

    excluded_trade_ids_json: list[int] = []

    methodology_notes: str = ""

    visibility: str = "private"

    active: bool = True


@router.post("")
def create_template(
    payload: CreateTemplateRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

    context = Depends(
        require_workspace_context(
            "claim_templates",
        )
    ),
):
    AuthorizationService.require_capability(
        context.access,
        REPORT_READ,
    )

    enforce_workspace_page_access(
        workspace_id=payload.workspace_id,
        db=db,
        page="claim_templates",
        action="create Claim Template",
    )

    preset = ClaimSchemaPreset(
        workspace_id=payload.workspace_id,
        name=payload.name,
        description=payload.description,
        preset_type=payload.template_type,
        included_member_ids_json=str(
            payload.included_member_ids_json
        ),
        included_symbols_json=str(
            payload.included_symbols_json
        ),
        methodology_notes=payload.methodology_notes,
        default_visibility=payload.visibility,
        is_system=False,
        is_active=payload.active,
    )

    db.add(preset)

    db.commit()

    db.refresh(preset)

    return {
        "id": preset.id,
        "status": "created",
    }


@router.get("/workspace/{workspace_id}")
def list_templates(
    workspace_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

    context = Depends(
        require_workspace_context(
            "claim_templates",
        )
    ),
):

    AuthorizationService.require_capability(
        context.access,
        REPORT_READ,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="claim_templates",
        action="access Claim Templates",
    )

    templates = (
        db.query(ClaimSchemaPreset)
        .filter(
            (ClaimSchemaPreset.workspace_id == workspace_id)
            | (ClaimSchemaPreset.is_system == True)
        )
        .all()
    )

    return templates


@router.get("/{template_id}")
def get_template(
    template_id: int
):
    return {
        "id": template_id
    }


@router.put("/{template_id}")
def update_template(
    template_id: int
):
    return {
        "status": "updated",
        "id": template_id
    }


@router.delete("/{template_id}")
def delete_template(
    template_id: int
):
    return {
        "status": "deleted",
        "id": template_id
    }