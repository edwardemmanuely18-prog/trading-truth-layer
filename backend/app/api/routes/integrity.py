from fastapi import (
    APIRouter,
    Depends,
)

from app.api.deps import (
    get_current_user,
)

from app.models.user import User

from app.services.authorization.engine.authorization_service import (
    AuthorizationService,
)

from app.api.authorization_deps import (
    require_workspace_context,
)

from app.services.authorization.registry.capability_catalog import (
    VERIFICATION_READ,
    VERIFICATION_EXECUTE,
)

from sqlalchemy.orm import Session

from app.core.db import get_db

from datetime import datetime

from app.models.integrity_scan import (
    IntegrityScan,
)

from app.models.claim_schema import (
    ClaimSchema,
)

from app.services.integrity_monitor_service import (
    scan_locked_claims,
)

from app.models.integrity_alert import (
    IntegrityAlert,
)

from app.services.integrity.integrity_dashboard_service import (
    build_integrity_dashboard,
)

router = APIRouter(
    prefix="/integrity",
    tags=["integrity"],
)


@router.post(
    "/scan/{workspace_id}"
)
def run_integrity_scan(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):  
    context = require_workspace_context(
        "integrity_analytics",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        VERIFICATION_EXECUTE,
    )

    claims_scanned = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .count()
    )

    before_count = (
        db.query(
            IntegrityAlert
        )
        .filter(
            IntegrityAlert.workspace_id
            == workspace_id
        )
        .count()
    )

    started_at = datetime.utcnow()

    scan_locked_claims(
        db,
        workspace_id,
    )

    after_count = (
        db.query(
            IntegrityAlert
        )
        .filter(
            IntegrityAlert.workspace_id
            == workspace_id
        )
        .count()
    )

    alerts_created = (
        after_count
        - before_count
    )

    scan = IntegrityScan(
        workspace_id=workspace_id,
        status="completed",
        claims_scanned=claims_scanned,
        alerts_found=alerts_created,
        summary_json=(
            f'{{"alerts_created": {alerts_created}}}'
        ),
        started_at=started_at,
        completed_at=datetime.utcnow(),
    )

    db.add(scan)
    db.commit()

    return {
        "workspace_id":
            workspace_id,

        "claims_scanned":
            claims_scanned,

        "alerts_created":
            alerts_created,

        "scan_id":
            scan.id,
    }


@router.get(
    "/history/{workspace_id}"
)
def integrity_scan_history(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    context = require_workspace_context(
        "integrity_analytics",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        VERIFICATION_READ,
    )

    scans = (
        db.query(IntegrityScan)
        .filter(
            IntegrityScan.workspace_id
            == workspace_id
        )
        .order_by(
            IntegrityScan.id.desc()
        )
        .all()
    )

    return [
        {
            "id":
                scan.id,

            "status":
                scan.status,

            "claims_scanned":
                scan.claims_scanned,

            "alerts_found":
                scan.alerts_found,

            "started_at":
                scan.started_at,

            "completed_at":
                scan.completed_at,
        }
        for scan in scans
    ]


@router.get(
    "/dashboard/{workspace_id}"
)
def integrity_dashboard(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    context = require_workspace_context(
        "integrity_analytics",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        VERIFICATION_READ,
    )

    return build_integrity_dashboard(
        db,
        workspace_id,
    )