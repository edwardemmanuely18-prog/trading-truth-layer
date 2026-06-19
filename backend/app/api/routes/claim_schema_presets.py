from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
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
):

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