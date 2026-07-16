from fastapi import APIRouter
from fastapi import Depends
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
from app.services.claim_schema_preset_service import (
    ensure_system_presets,
)

router = APIRouter()


@router.get(
    "/workspaces/{workspace_id}/claim-presets"
)
def get_claim_presets(
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

    ensure_system_presets(
        db,
        workspace_id,
    )
    
    presets = (
        db.query(
            ClaimSchemaPreset
        )
        .filter(
            ClaimSchemaPreset.workspace_id
            == workspace_id,
            ClaimSchemaPreset.is_active
            == True,
        )
        .order_by(
            ClaimSchemaPreset.name.asc()
        )
        .all()
    )

    return [
        {
            "id": preset.id,
            "name": preset.name,
            "description":
                preset.description,
            "preset_type":
                preset.preset_type,
            "included_member_ids_json":
                preset.included_member_ids_json,
            "included_symbols_json":
                preset.included_symbols_json,
            "methodology_notes":
                preset.methodology_notes,
            "default_visibility":
                preset.default_visibility,
            "is_system":
                preset.is_system,
        }
        for preset in presets
    ]