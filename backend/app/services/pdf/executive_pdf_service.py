from __future__ import annotations

from io import BytesIO

import hashlib
import json

from app.services.report_registry.models import (
    ReportType,
)

from app.services.report_registry.report_registry_service import (
    ReportRegistryService,
)

from app.services.investigations.facade import (
    InvestigationFacade,
)

from app.services.pdf.executive.generator import (
    generate_executive_report_pdf,
)


# ==========================================================
# Executive PDF Service
# ==========================================================

def generate_executive_pdf(
    workspace_id: int,
    db,
):
    """
    Generates the Executive Investigation Report.

    Mirrors the Institutional Investigation
    PDF architecture.
    """

    report = InvestigationFacade.workspace(

        db=db,

        workspace_id=workspace_id,

    )

    report_hash = hashlib.sha256(

        json.dumps(

            report,

            default=str,

            sort_keys=True,

        ).encode()

    ).hexdigest()

    registry = ReportRegistryService(
        db,
    )

    reserved_report = registry.reserve_report(

        report_type=ReportType.EXECUTIVE,

        workspace_id=workspace_id,

    )

    verification_url = (

        reserved_report.verification_url

    )

    pdf_bytes = generate_executive_report_pdf(

        report=report,

        verification_url=verification_url,

    )

    metadata = {

        #
        # Registry
        #

        "classification":
            "Executive Investigation Summary Report",

        "registry_state":
            "REGISTERED",

        "certificate_version":
            "1",

        "tvs_version":
            "1.0",

        #
        # Executive status
        #

        "verification_status":
            str(report.status.value),

        #
        # Summary
        #

        "investigation_summary":
            getattr(
                report.summary,
                "executive_summary",
                None,
            ),

        #
        # Investigation statistics
        #

        "critical_findings":
            len(report.findings),

        "recommendations":
            len(report.recommendations),

        "provider_count":
            report.metadata.get(
                "provider_count",
            ),

        "total_nodes":
            report.metadata.get(
                "total_nodes",
            ),

        #
        # Investigation metadata
        #

        "scope":
            report.metadata.get(
                "scope",
            ),

        "allocator_decision":
            getattr(
                report.summary,
                "allocator_decision",
                None,
            ),

        "overall_risk":
            getattr(
                report.summary,
                "overall_risk",
                None,
            ),

        "investigation_confidence":
            getattr(
                report.summary,
                "investigation_confidence",
                None,
            ),

        #
        # Fingerprint
        #

        "report_hash":
            report_hash,

    }

    buffer = BytesIO(

        pdf_bytes,

    )

    buffer.seek(

        0,

    )

    registry.finalize_report(

        reserved_report=reserved_report,

        report_title=(

            "Executive Investigation Summary Report"

        ),

        file_name=(

            f"executive_investigation_report_"
            f"{workspace_id}.pdf"

        ),

        pdf_bytes=pdf_bytes,

        metadata=metadata,

    )

    return (

        buffer,

        f"executive_investigation_report_{workspace_id}.pdf",

    )


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def build_executive_pdf(
    workspace_id: int,
    db,
):

    return generate_executive_pdf(

        workspace_id,

        db,

    )