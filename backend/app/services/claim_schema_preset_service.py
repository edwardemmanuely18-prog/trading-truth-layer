from sqlalchemy.orm import Session

from app.models.claim_schema_preset import (
    ClaimSchemaPreset,
)


def ensure_system_presets(
    db: Session,
    workspace_id: int,
):
    existing = (
        db.query(
            ClaimSchemaPreset
        )
        .filter(
            ClaimSchemaPreset.workspace_id
            == workspace_id
        )
        .count()
    )

    if existing:
        return

    presets = [

        ClaimSchemaPreset(
            workspace_id=workspace_id,
            name="Monthly Verification",
            description="Standard monthly verification workflow.",
            preset_type="monthly",
            included_symbols_json="[]",
            methodology_notes="Monthly verification review.",
            is_system=True,
        ),

        ClaimSchemaPreset(
            workspace_id=workspace_id,
            name="Quarterly Verification",
            description="Quarterly performance review.",
            preset_type="quarterly",
            included_symbols_json="[]",
            methodology_notes="Quarterly verification review.",
            is_system=True,
        ),

        ClaimSchemaPreset(
            workspace_id=workspace_id,
            name="Annual Verification",
            description="Annual trust-grade verification.",
            preset_type="annual",
            included_symbols_json="[]",
            methodology_notes="Annual verification review.",
            is_system=True,
        ),
    ]

    db.add_all(presets)

    db.commit()