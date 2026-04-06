from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db

router = APIRouter(prefix="/workspaces", tags=["platform"])


@router.get("/{workspace_id}/platform-readiness")
def get_platform_readiness(workspace_id: int, db: Session = Depends(get_db)):
    """
    Phase 6: Platform readiness + integration surface

    This is a placeholder foundation endpoint.
    It will later connect to:
    - broker integrations
    - API keys
    - webhook ingestion
    - external verification exposure
    """

    return {
        "workspace_id": workspace_id,
        "capabilities": {
            "public_verification_enabled": True,
            "public_distribution_enabled": True,
            "external_verification_enabled": True,
            "api_access_enabled": False,
            "broker_import_enabled": False,
            "webhook_ingestion_enabled": False,
        },
        "integration_sources": [],
        "verification_exposure_level": "public",
        "recommended_next_step": "Connect a broker or enable API access to activate external verification pipelines.",
    }