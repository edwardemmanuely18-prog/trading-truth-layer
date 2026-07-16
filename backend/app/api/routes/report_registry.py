from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from fastapi.responses import (
    JSONResponse,
    StreamingResponse,
)

from fastapi.responses import HTMLResponse

from app.services.report_registry.verification_page import (
    build_verification_page,
)

from io import BytesIO

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.services.report_registry.repositories.report_registry_repository import (
    ReportRegistryRepository,
)

from app.services.report_registry.storage import (
    load_report,
    report_exists,
)

router = APIRouter(
    tags=["Report Registry"],
)


# ==========================================================
# Public Verification
# ==========================================================

@router.get(
    "/report/{report_id}",
)
def verify_report(
    report_id: str,
    db: Session = Depends(get_db),
):

    repository = ReportRegistryRepository(
        db,
    )

    report = repository.get_by_report_id(
        report_id,
    )

    if report is None:

        raise HTTPException(

            status_code=404,

            detail="Report not found.",

        )

    html = build_verification_page(
        report,
    )

    return HTMLResponse(
        content=html,
    )


# ==========================================================
# Download
# ==========================================================

@router.get(
    "/report/{report_id}/download",
)
def download_report(
    report_id: str,
    db: Session = Depends(get_db),
):

    repository = ReportRegistryRepository(
        db,
    )

    report = repository.get_by_report_id(
        report_id,
    )

    if report is None:

        raise HTTPException(

            status_code=404,

            detail="Report not found.",

        )

    if not report_exists(

        storage_key=report.storage_key,

    ):

        raise HTTPException(

            status_code=404,

            detail="Stored PDF not found.",

        )

    repository.register_download(
        report_id,
    )

    pdf = load_report(

        storage_key=report.storage_key,

    )

    return StreamingResponse(

        BytesIO(pdf),

        media_type="application/pdf",

        headers={

            "Content-Disposition":
                f'inline; filename="{report.file_name}"',

        },

    )


# ==========================================================
# Machine API
# ==========================================================

@router.get(
    "/api/report/{report_id}",
)
def report_api(
    report_id: str,
    db: Session = Depends(get_db),
):

    repository = ReportRegistryRepository(
        db,
    )

    report = repository.get_by_report_id(
        report_id,
    )

    if report is None:

        raise HTTPException(

            status_code=404,

            detail="Report not found.",

        )

    return {

        "report_id": report.report_id,

        "type": report.report_type,

        "status": report.status,

        "workspace_id": report.workspace_id,

        "sha256": report.sha256,

        "verification_url": report.verification_url,

        "metadata": report.metadata_json,

    }