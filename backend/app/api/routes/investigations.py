from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.user import User

from app.api.deps import (
    get_current_user,
)

from app.services.authorization.engine.authorization_service import (
    AuthorizationService,
)

from app.services.authorization.registry.capability_catalog import (
    INVESTIGATION_READ,
)

from app.api.authorization_deps import (
    require_workspace_context,
)

from app.services.entitlements import (
    enforce_workspace_page_access,
)

from app.services.investigations.facade import (
    InvestigationFacade,
)

from app.services.investigations.report_builder import (
    InvestigationReportBuilder,
)


router = APIRouter(

    prefix="/investigations",

    tags=["Institutional Investigations"],

)


# ============================================================
# Common Authorization
# ============================================================

def require_investigation_access(

    workspace_id: int,

    db: Session,

    current_user: User,

):

    context = require_workspace_context(

        "institutional_investigation",

    )(

        workspace_id=workspace_id,

        db=db,

        current_user=current_user,

    )

    AuthorizationService.require_capability(

        context.access,

        INVESTIGATION_READ,

    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="investigations",
        action="access Institutional Investigation System",
    )

    return context


# ============================================================
# Workspace Investigation
# ============================================================

@router.get(
    "/workspaces/{workspace_id}"
)
def get_workspace_investigation(

    workspace_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.workspace(
        db=db,
        workspace_id=workspace_id,
    )

    return InvestigationReportBuilder.build(report)


# ============================================================
# Claim Investigation
# ============================================================

@router.get(
    "/workspaces/{workspace_id}/claims/{claim_id}"
)
def get_claim_investigation(

    workspace_id: int,

    claim_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.claim(

        db=db,

        workspace_id=workspace_id,

        claim_id=claim_id,

    )

    return InvestigationReportBuilder.build(report)


# ============================================================
# Member Investigation
# ============================================================

@router.get(
    "/workspaces/{workspace_id}/members/{member_id}"
)
def get_member_investigation(

    workspace_id: int,

    member_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.member(

        db=db,

        workspace_id=workspace_id,

        member_id=member_id,

    )

    return InvestigationReportBuilder.build(report)


# ============================================================
# Account Investigation
# ============================================================

@router.get(
    "/workspaces/{workspace_id}/accounts/{account_id}"
)
def get_account_investigation(

    workspace_id: int,

    account_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.account(

        db=db,

        workspace_id=workspace_id,

        account_id=account_id,

    )

    return InvestigationReportBuilder.build(report)


# ============================================================
# Broker Investigation
# ============================================================

@router.get(
    "/workspaces/{workspace_id}/brokers/{broker_connection_id}"
)
def get_broker_investigation(

    workspace_id: int,

    broker_connection_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.broker(

        db=db,

        workspace_id=workspace_id,

        broker_connection_id=broker_connection_id,

    )

    return InvestigationReportBuilder.build(report)


# ============================================================
# Sync Job Investigation
# ============================================================

@router.get(
    "/workspaces/{workspace_id}/sync-jobs/{sync_job_id}"
)
def get_sync_job_investigation(

    workspace_id: int,

    sync_job_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.sync_job(

        db=db,

        workspace_id=workspace_id,

        sync_job_id=sync_job_id,

    )

    return InvestigationReportBuilder.build(report)


# ============================================================
# Strategy Investigation
# ============================================================

@router.get(
    "/workspaces/{workspace_id}/strategies/{strategy_id}"
)
def get_strategy_investigation(

    workspace_id: int,

    strategy_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.strategy(

        db=db,

        workspace_id=workspace_id,

        strategy_id=strategy_id,

    )

    return InvestigationReportBuilder.build(report)


# ============================================================
# Investigation Overview
# ============================================================

@router.get(
    "/workspaces/{workspace_id}/overview"
)
def get_investigation_overview(

    workspace_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.workspace(

        db=db,

        workspace_id=workspace_id,

    )

    critical_findings = sum(

        1

        for finding in report.findings

        if getattr(
            finding,
            "severity",
            "",
        ).upper() == "CRITICAL"

    )

    return {

        "score": report.summary.investigation_confidence,

        "total_findings": len(
            report.findings,
        ),

        "critical_findings": critical_findings,

        "graph_relationships":
            len(report.graph.relationships),

        "timeline_events": 0,

        "generated_at": report.generated_at,

    }


# ============================================================
# Investigation Domains
# ============================================================

@router.get(
    "/workspaces/{workspace_id}/domains"
)
def get_investigation_domains(

    workspace_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.workspace(

        db=db,

        workspace_id=workspace_id,

    )

    return {

        "execution": report.execution,

        "evidence": report.evidence,

        "verification": report.verification,

        "governance": report.governance,

        "broker": report.broker,

        "synchronization": report.synchronization,

        "review": report.review,

        "behavior": report.behavior,

        "allocator": report.allocator,

    }


# ============================================================
# Investigation Allocator
# ============================================================

@router.get(
    "/workspaces/{workspace_id}/allocator"
)
def get_investigation_allocator(

    workspace_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.workspace(

        db=db,

        workspace_id=workspace_id,

    )

    return report.allocator


# ============================================================
# Verification Investigation
# ============================================================

@router.get(
    "/workspaces/{workspace_id}/verification"
)
def get_verification_investigation(

    workspace_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user,
    ),

):

    require_investigation_access(

        workspace_id,

        db,

        current_user,

    )

    report = InvestigationFacade.workspace(

        db=db,

        workspace_id=workspace_id,

    )

    return report.verification