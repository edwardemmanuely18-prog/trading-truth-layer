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

from app.services.pdf.investigation.generator import (
    generate_investigation_report_pdf,
)


# ==========================================================
# Institutional Investigation PDF Service
# ==========================================================


def generate_investigation_pdf(
    workspace_id: int,
    db,
):
    """
    Generates the canonical Institutional Investigation
    Report (IIR).

    This service is intentionally lightweight.

    It delegates all investigation construction to the
    Investigation Facade and all PDF rendering to the
    Investigation PDF Generator.
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

        report_type=ReportType.INVESTIGATION,

        workspace_id=workspace_id,

    )

    verification_url = (
        reserved_report.verification_url
    )

    pdf_bytes = generate_investigation_report_pdf(

        report=report,

        verification_url=verification_url,

    )

    metadata = {

        #
        # Registry
        #

        "classification":
            "Institutional Investigation Report",

        "registry_state":
            "REGISTERED",

        "certificate_version":
            "1",

        "tvs_version":
            "1.0",

        #
        # Investigation status
        #

        "verification_status":
            str(report.status.value),

        #
        # Investigation summary
        #

        "investigation_summary":
            getattr(
                report.summary,
                "executive_summary",
                None,
            ),

        #
        # Findings
        #

        "critical_findings":
            len(report.findings),

        "recommendations":
            len(report.recommendations),

        #
        # IIS statistics
        #

        "provider_count":
            report.metadata.get(
                "provider_count",
            ),

        "total_nodes":
            report.metadata.get(
                "total_nodes",
            ),

        #
        # Metadata
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
            "Institutional Investigation Report"
        ),

        file_name=(
            f"institutional_investigation_report_"
            f"{workspace_id}.pdf"
        ),

        pdf_bytes=pdf_bytes,

        metadata=metadata,

    )

    return (

        buffer,

        f"institutional_investigation_report_{workspace_id}.pdf",

    )


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================


def build_investigation_pdf(
    workspace_id: int,
    db,
):
    """
    Backward-compatible entry point.

    API routes should import this function.
    """

    return generate_investigation_pdf(

        workspace_id,

        db,

    )