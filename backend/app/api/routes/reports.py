from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.db import get_db

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

from fastapi.responses import StreamingResponse

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
):
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
):
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
):
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
):
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
):
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
):
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
):
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
):

    print("========== ALLOCATOR REPORT ROUTE ==========")
    print("Workspace:", workspace_id)
    
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