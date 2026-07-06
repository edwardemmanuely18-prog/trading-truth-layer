from io import BytesIO
import hashlib
import json

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

    print("HEADER 1")
    draw_watermark(canvas)

    print("HEADER 2")
    draw_header(
        canvas,
        title="Allocator Due Diligence Report",
        subtitle="Trading Truth Layer",
        tvs_version="TVS 1.0",
    )

    print("HEADER 3")
    draw_footer(
        canvas,
        doc,
        report_hash="",
    )

    print("HEADER 4")
    draw_verified_stamp(canvas)

    print("HEADER 5")
    draw_hash_watermark(
        canvas,
        report_hash="",
    )

    print("HEADER COMPLETE")


def generate_allocator_report_pdf(
    workspace_id: int,
    db,
):
    print("STEP 1")

    report = build_allocator_report_payload(
        workspace_id,
        db,
    )

    print("STEP 2")

    report_hash = hashlib.sha256(
        json.dumps(
            report,
            default=str,
            sort_keys=True,
        ).encode()
    ).hexdigest()

    print("STEP 3")

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

    print("Cover")

    story.extend(
        build_cover_page(
            report,
            workspace_id,
            report_hash,
        )
    )

    print("Executive")

    section = build_executive_summary(report)

    print("\n===== EXECUTIVE SUMMARY =====")
    for i, item in enumerate(section):
        print(i, type(item))
    print("=============================\n")

    story.extend(section)

    print("Performance")

    section = build_performance_section(report)

    print("\n===== PERFORMANCE =====")
    for i, item in enumerate(section):
        print(i, type(item))
    print("=======================\n")

    story.extend(section)

    print("Risk")

    section = build_risk_section(report)

    print("\n===== RISK =====")
    for i, item in enumerate(section):
        print(i, type(item))
    print("================\n")

    story.extend(section)

    print("Verification")

    section = build_verification_section(report)

    print("\n===== VERIFICATION =====")
    for i, item in enumerate(section):
        print(i, type(item))
    print("========================\n")

    story.extend(section)

    print("Governance")

    section = build_governance_section(report)

    print("\n===== GOVERNANCE =====")
    for i, item in enumerate(section):
        print(i, type(item))
    print("======================\n")

    story.extend(section)

    print("Findings")

    section = build_findings_section(report)

    print("\n===== FINDINGS =====")
    for i, item in enumerate(section):
        print(i, type(item))
    print("====================\n")

    story.extend(section)

    verification_url = (
        f"https://tradingtruthlayer.com/"
        f"workspace/{workspace_id}/report-center"
    )

    print("Verdict")

    section = build_verdict_section(
        report,
        report_hash,
        verification_url,
    )

    print("\n===== VERDICT =====")
    for i, item in enumerate(section):
        print(i, type(item))
    print("===================\n")

    story.extend(section)

    print("\n===== STORY VALIDATION =====")

    for i, item in enumerate(story):
        print(i, type(item))

        if isinstance(item, list):
            print(">>> NESTED LIST FOUND AT INDEX", i)

    print("============================\n")

    print("Building PDF")

    doc.build(

        story,

        onFirstPage=lambda c, d: draw_watermark(c),

        onLaterPages=_draw_header_footer,

    )

    print("PDF BUILD FINISHED")

    buffer.seek(0)

    return (
        buffer,
        f"allocator_report_{workspace_id}.pdf",
    )

    print("Done")


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