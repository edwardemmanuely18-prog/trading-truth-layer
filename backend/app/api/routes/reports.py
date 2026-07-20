from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.api.authorization_deps import (
    require_workspace_context,
)

from app.api.deps import (
    get_current_user,
)

from app.models.user import User

from app.services.authorization.engine.authorization_service import (
    AuthorizationService,
)

from app.services.authorization.registry.capability_catalog import (
    REPORT_READ,
)

from app.services.entitlements import (
    enforce_workspace_page_access,
    enforce_workspace_feature,
)

from app.services.reports.due_diligence_report_service import (
    build_due_diligence_report_payload,
)

from app.services.reports.verification_report_service import (
    build_verification_report_payload,
)

from app.services.reports.audit_report_service import (
    build_audit_report_payload,
)

from app.services.reports.allocator_report_service import (
    build_allocator_report_payload,
)

from fastapi.responses import (
    StreamingResponse,
)

from app.services.pdf.due_diligence_pdf_service import (
    build_due_diligence_pdf,
)

from app.services.pdf.verification_pdf_service import (
    build_verification_pdf,
)

from app.services.pdf.audit_pdf_service import (
    build_audit_pdf,
)

from app.services.pdf.allocator_pdf_service import (
    build_allocator_pdf,
)

from app.services.pdf.investigation_pdf_service import (
    build_investigation_pdf,
)

from app.services.pdf.executive_pdf_service import (
    build_executive_pdf,
)

from app.services.pdf.guidebooks.volume_1.volume_1_pdf_service import (
    generate_volume_1_pdf,
)

from app.services.pdf.guidebooks.volume_2.volume_2_pdf_service import (
    generate_volume_2_pdf,
)

from app.services.pdf.guidebooks.volume_3.volume_3_pdf_service import (
    generate_volume_3_pdf,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/workspace/{workspace_id}/due-diligence"
)
def get_due_diligence_report(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    context = Depends(
        require_workspace_context(
            "report_center",
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
        page="report_center",
        action="access Report Center",
    )

    return (
        build_due_diligence_report_payload(
            workspace_id,
            db,
        )
    )


@router.get(
    "/workspace/{workspace_id}/verification"
)
def get_verification_report(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    context = Depends(
        require_workspace_context(
            "report_center",
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
        page="report_center",
        action="access Report Center",
    )

    return (
        build_verification_report_payload(
            workspace_id,
            db,
        )
    )


@router.get(
    "/workspace/{workspace_id}/audit"
)
def get_audit_report(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    context = Depends(
        require_workspace_context(
            "report_center",
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
        page="report_center",
        action="access Report Center",
    )

    return (
        build_audit_report_payload(
            workspace_id,
            db,
        )
    )


@router.get(
    "/workspace/{workspace_id}/allocator"
)
def get_allocator_report(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    context = Depends(
        require_workspace_context(
            "report_center",
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
        page="report_center",
        action="access Report Center",
    )

    return (
        build_allocator_report_payload(
            workspace_id,
            db,
        )
    )


@router.get(
    "/workspace/{workspace_id}/due-diligence/download"
)
def download_due_diligence_report(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    context = Depends(
        require_workspace_context(
            "report_center",
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
        page="report_center",
        action="access Report Center",
    )

    pdf_buffer, filename = (
        build_due_diligence_pdf(
            workspace_id,
            db,
        )
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


@router.get(
    "/workspace/{workspace_id}/verification/download"
)
def download_verification_report(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    context = Depends(
        require_workspace_context(
            "report_center",
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
        page="report_center",
        action="access Report Center",
    )

    pdf_buffer, filename = (
        build_verification_pdf(
            workspace_id,
            db,
        )
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


@router.get(
    "/workspace/{workspace_id}/audit/download"
)
def download_audit_report(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    context = Depends(
        require_workspace_context(
            "report_center",
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
        page="report_center",
        action="access Report Center",
    )

    pdf_buffer, filename = (
        build_audit_pdf(
            workspace_id,
            db,
        )
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


@router.get(
    "/workspace/{workspace_id}/allocator/download"
)
def download_allocator_report(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    context = Depends(
        require_workspace_context(
            "report_center",
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
        page="report_center",
        action="access Report Center",
    )

    enforce_workspace_feature(
        workspace_id=workspace_id,
        db=db,
        feature="allocator_report_pdf",
        action="download Allocator Report PDF",
    )
    
    pdf_buffer, filename = (
        build_allocator_pdf(
            workspace_id,
            db,
        )
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


@router.get(
    "/workspace/{workspace_id}/investigation/download"
)
def download_investigation_report(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    context=Depends(
        require_workspace_context(
            "report_center",
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
        page="report_center",
        action="download Investigation Report",
    )

    pdf_buffer, filename = (
        build_investigation_pdf(
            workspace_id,
            db,
        )
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


@router.get(
    "/workspace/{workspace_id}/executive/download",
)
def download_executive_report(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    context=Depends(
        require_workspace_context(
            "report_center",
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
        page="report_center",
        action="download Executive Report",
    )

    #
    # Business-plan entitlement
    # (same entitlement pattern used by
    # Investigation Reports)
    #

    pdf_buffer, filename = (
        build_executive_pdf(
            workspace_id,
            db,
        )
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


# ==========================================================
# TTL GUIDEBOOK SERIES
# ==========================================================


@router.get(
    "/guidebooks/volume-1/download",
)
def download_guidebook_volume_1():

    """
    Public endpoint for downloading
    Trading Truth Layer Guidebook Series
    Volume I.

    No authentication or workspace
    context is required.
    """

    pdf_buffer, filename = (
        generate_volume_1_pdf()
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


# ==========================================================
# TTL GUIDEBOOK SERIES - VIEW
# ==========================================================


@router.get(
    "/guidebooks/volume-1/view",
)
def view_guidebook_volume_1():

    """
    Public endpoint for viewing
    Trading Truth Layer Guidebook Series
    Volume I directly in the browser.

    No authentication or workspace
    context is required.
    """

    pdf_buffer, filename = (
        generate_volume_1_pdf()
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'inline; filename="{filename}"'
        },
    )


# ==========================================================
# TTL GUIDEBOOK SERIES - VOLUME II DOWNLOAD
# ==========================================================


@router.get(
    "/guidebooks/volume-2/download",
)
def download_guidebook_volume_2():

    """
    Public endpoint for downloading
    Trading Truth Layer Guidebook Series
    Volume II.

    No authentication or workspace
    context is required.
    """

    pdf_buffer, filename = (
        generate_volume_2_pdf()
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


# ==========================================================
# TTL GUIDEBOOK SERIES - VOLUME II VIEW
# ==========================================================


@router.get(
    "/guidebooks/volume-2/view",
)
def view_guidebook_volume_2():

    """
    Public endpoint for viewing
    Trading Truth Layer Guidebook Series
    Volume II directly in the browser.

    No authentication or workspace
    context is required.
    """

    pdf_buffer, filename = (
        generate_volume_2_pdf()
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'inline; filename="{filename}"'
        },
    )


# ==========================================================
# TTL GUIDEBOOK SERIES - VOLUME III DOWNLOAD
# ==========================================================


@router.get(
    "/guidebooks/volume-3/download",
)
def download_guidebook_volume_3():

    pdf_buffer, filename = (
        generate_volume_3_pdf()
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


# ==========================================================
# TTL GUIDEBOOK SERIES - VOLUME III VIEW
# ==========================================================


@router.get(
    "/guidebooks/volume-3/view",
)
def view_guidebook_volume_3():

    pdf_buffer, filename = (
        generate_volume_3_pdf()
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'inline; filename="{filename}"'
        },
    )


