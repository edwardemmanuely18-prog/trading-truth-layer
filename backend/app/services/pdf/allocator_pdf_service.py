from io import BytesIO
import hashlib
import json

from app.services.report_registry.models import (
    ReportType,
)

from app.services.report_registry.report_registry_service import (
    ReportRegistryService,
)

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate

from app.services.reports.allocator_report_service import (
    build_allocator_report_payload,
)

from app.services.pdf.common.institutional_header_footer import (
    draw_header,
    draw_footer,
)

from app.services.pdf.common.institutional_watermark import (
    draw_watermark,
    draw_verified_stamp,
    draw_hash_watermark,
)

from app.services.pdf.allocator.cover import (
    build_cover_page,
)

from app.services.pdf.allocator.executive_summary import (
    build_executive_summary,
)

from app.services.pdf.allocator.performance import (
    build_performance_section,
)

from app.services.pdf.allocator.risk import (
    build_risk_section,
)

from app.services.pdf.allocator.governance import (
    build_governance_section,
)

from app.services.pdf.allocator.verification import (
    build_verification_section,
)

from app.services.pdf.allocator.findings import (
    build_findings_section,
)

from app.services.pdf.allocator.verdict import (
    build_verdict_section,
)

from app.services.pdf.common.institutional_theme import (
    PAGE_MARGIN,
    TOP_MARGIN,
    BOTTOM_MARGIN,
    HEADER_HEIGHT,
    FOOTER_HEIGHT,
)


def _draw_header_footer(canvas, doc):

    draw_watermark(canvas)

    draw_header(
        canvas,
        title="Allocator Due Diligence Report",
        subtitle="Trading Truth Layer",
        tvs_version="TVS 1.0",
    )

    draw_footer(
        canvas,
        doc,
        report_hash="",
    )


    draw_verified_stamp(canvas)

   
    draw_hash_watermark(
        canvas,
        report_hash="",
    )



def generate_allocator_report_pdf(
    workspace_id: int,
    db,
):

    report = build_allocator_report_payload(
        workspace_id,
        db,
    )

    import pprint

    registry = ReportRegistryService(
        db,
    )

    reserved_report = registry.reserve_report(

        report_type=ReportType.ALLOCATOR,

        workspace_id=workspace_id,

    )

    verification_url = (

        reserved_report.verification_url

    )

    report_hash = hashlib.sha256(
        json.dumps(
            report,
            default=str,
            sort_keys=True,
        ).encode()
    ).hexdigest()

   
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,

        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,

        topMargin=TOP_MARGIN + 12,

        bottomMargin=BOTTOM_MARGIN + FOOTER_HEIGHT,
    )

    story = []

    story.extend(

        build_cover_page(

            report=report,

            workspace_id=workspace_id,

            report_hash=report_hash,

            verification_url=verification_url,

        )

    )

    section = build_executive_summary(report)

    story.extend(section)


    section = build_performance_section(report)

    story.extend(section)


    section = build_risk_section(report)

    story.extend(section)

    section = build_verification_section(report)

    story.extend(section)

    section = build_governance_section(report)

    story.extend(section)

    section = build_findings_section(report)

    story.extend(section)

    section = build_verdict_section(
        report,
        report_hash,
        verification_url,
    )

    story.extend(section)


    doc.build(

        story,

        onFirstPage=lambda c, d: draw_watermark(c),

        onLaterPages=_draw_header_footer,

    )

    #
    # Verification metadata
    #

    allocator = report.get(
        "allocator_assessment",
        {},
    )

    verification = report.get(
        "verification",
        {},
    )

    workspace_verification = report.get(
        "workspace_verification",
    )

    #
    # Workspace verification helpers
    #

    if workspace_verification:

        evidence_component = (
            workspace_verification.evidence
        )

        integrity_component = (
            workspace_verification.integrity
        )

        governance_component = (
            workspace_verification.governance
        )

        transparency_component = (
            workspace_verification.transparency
        )

        network_component = (
            workspace_verification.network
        )

        reviews_component = (
            workspace_verification.reviews
        )

        disputes_component = (
            workspace_verification.disputes
        )

        stability_component = (
            workspace_verification.stability
        )

    else:

        evidence_component = None
        integrity_component = None
        governance_component = None
        transparency_component = None
        network_component = None
        reviews_component = None
        disputes_component = None
        stability_component = None

    verification_certificate = report.get(
        "verification_certificate",
    )

    certificate = None


    #
    # Multiple certificates
    #

    if isinstance(
        verification_certificate,
        list,
    ):

        if verification_certificate:

            certificate = (
                verification_certificate[0]
            )


    #
    # Single certificate
    #

    elif verification_certificate is not None:

        certificate = (
            verification_certificate
        )

    pdf_bytes = buffer.getvalue()

    #
    # Evidence tier
    #

    verification_tier = None
    verification_status = None
    evidence_tier = None


    if workspace_verification:

        #
        # Workspace aggregated evidence tier.
        #

        evidence_tier = (
            workspace_verification.evidence.status
        )

        #
        # Workspace verification status.
        #

        verification_status = (
            workspace_verification.verification_band
        )

        #
        # Aggregated tier distribution.
        #

        tier_distribution = (
            workspace_verification.tier_distribution
        )

        if tier_distribution:

            verification_tier = max(

                tier_distribution,

                key=tier_distribution.get,

            )

    
    #
    # Allocator metadata
    #

    allocator_metadata = {

        #
        # Report metadata
        #

        "classification":
            "Institutional Due Diligence Report",

        "registry_state":
            "REGISTERED",

        "certificate_version":
            "1",

        "tvs_version":
            "1.0",

        #
        # Allocator assessment
        #

        "verification_score":

            verification.get(
                "verification_score",
            ),

        "allocator_score":

            allocator.get(
                "allocator_score",
            ),

        "allocator_grade":
            allocator.get(
                "allocator_band",
            ),

        "institutional_ready":

            "YES"
            if allocator.get(
                "allocation_capacity"
            ) == "APPROVED"
            else "NO",

        "review_required":

            "YES"
            if allocator.get(
                "allocator_band"
            ) == "HIGH REVIEW"
            else "NO",

        "capital_allocation":

            allocator.get(
                "allocation_capacity",
            ),

        #
        # TVS assessment
        #

        "verification_band":
            (
                workspace_verification.verification_band
                if workspace_verification
                else None
            ),

        "verification_status":
            verification_status,

        "verification_tier":
            verification_tier,

        #
        # Workspace level reports do not expose
        # claim provenance.
        #

        "primary_evidence":
            "Aggregated Workspace Claims",

        "evidence_source":
            "Trading Truth Layer TVS",

        "evidence_tier":
            evidence_tier,

        #
        # Portfolio verification
        #

        "verified_claims":
            (
                workspace_verification.claim_count
                if workspace_verification
                else None
            ),

        "verified_trades":

            verification.get(
                "broker_verified",
            ),

        "average_verification_score":

            (
                workspace_verification.average_verification_score
                if workspace_verification
                else None
            ),

        #
        # Governance metrics
        #

        "integrity":

            (
                integrity_component.details.get(
                    "average_percentage",
                )
                if integrity_component
                else None
            ),

        "governance":

            (
                governance_component.details.get(
                    "average_percentage",
                )
                if governance_component
                else None
            ),

        "transparency":

            (
                transparency_component.details.get(
                    "average_percentage",
                )
                if transparency_component
                else None
            ),

        "network":

            (
                network_component.details.get(
                    "average_percentage",
                )
                if network_component
                else None
            ),

        "reviews":

            (
                reviews_component.details.get(
                    "average_percentage",
                )
                if reviews_component
                else None
            ),

        "disputes":

            (
                disputes_component.details.get(
                    "average_percentage",
                )
                if disputes_component
                else None
            ),

        "stability":

            (
                stability_component.details.get(
                    "average_percentage",
                )
                if stability_component
                else None
            ),

    }

    registry.finalize_report(

        reserved_report=reserved_report,

        report_title=(
            "Allocator Due Diligence Report"
        ),

        file_name=(
            f"allocator_report_{workspace_id}.pdf"
        ),

        pdf_bytes=pdf_bytes,

        metadata=allocator_metadata,

    )

    return (

        BytesIO(pdf_bytes),

        f"allocator_report_{workspace_id}.pdf",

    )



# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def build_allocator_pdf(
    workspace_id: int,
    db,
):
    """
    Backward-compatible entry point.

    Existing API routes import this function.
    """

    return generate_allocator_report_pdf(
        workspace_id,
        db,
    )