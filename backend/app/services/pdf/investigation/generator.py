from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    PageBreak,
)

from app.services.investigations.models import (
    InvestigationReport,
)

from app.services.pdf.common.institutional_header_footer import (
    draw_footer,
    draw_header,
)

from app.services.pdf.common.institutional_theme import (
    PAGE_MARGIN,
    TOP_MARGIN,
    BOTTOM_MARGIN,
    FOOTER_HEIGHT,
)

from app.services.pdf.common.institutional_watermark import (
    draw_verified_stamp,
    draw_watermark,
)

from .cover import (
    build_investigation_cover,
)

from .executive_summary import (
    build_investigation_executive_summary,
)

from .metadata import (
    build_investigation_metadata,
)

from .pipeline import (
    build_investigation_pipeline,
)

from .graph import (
    build_investigation_graph,
)

from .domains import (
    build_investigation_domains,
)

from .findings import (
    build_investigation_findings,
)

from .critical_path import (
    build_investigation_critical_path,
)

from .recommendations import (
    build_investigation_recommendations,
)

from .allocator import (
    build_investigation_allocator,
)

from .verdict import (
    build_institutional_verdict,
)

from .appendix import (
    build_investigation_appendix,
)


# ==========================================================
# HEADER / FOOTER
# ==========================================================

def _draw_header_footer(
    canvas,
    doc,
):

    draw_watermark(canvas)

    draw_header(
        canvas,
        title="Institutional Investigation Report",
        subtitle="Investigation Intelligence System",
        tvs_version="IIS 1.0",
    )

    draw_footer(
        canvas,
        doc,
        report_hash="",
    )

    draw_verified_stamp(canvas)


# ==========================================================
# GENERATOR
# ==========================================================

def generate_investigation_report_pdf(
    *,
    report: InvestigationReport,
    verification_url: str,
) -> bytes:

    buffer = BytesIO()

    doc = SimpleDocTemplate(

        buffer,

        pagesize=letter,

        leftMargin=PAGE_MARGIN,

        rightMargin=PAGE_MARGIN,

        topMargin=TOP_MARGIN + 28,

        bottomMargin=BOTTOM_MARGIN + FOOTER_HEIGHT,

    )

    story = []

    #
    # COVER
    #

    build_investigation_cover(
        story,
        report,
        verification_url,
    )

    story.append(PageBreak())

    #
    # EXECUTIVE
    #

    build_investigation_executive_summary(
        story,
        report,
    )

    build_investigation_metadata(
        story,
        report,
    )

    build_investigation_pipeline(
        story,
        report,
    )

    #
    # INVESTIGATION
    #

    build_investigation_graph(
        story,
        report,
    )

    #
    # Begin the detailed institutional investigation
    # on a fresh page.
    #

    story.append(
        PageBreak()
    )

    build_investigation_domains(
        story,
        report,
    )

    build_investigation_findings(
        story,
        report,
    )

    build_investigation_critical_path(
        story,
        report,
    )

    #
    # DECISION
    #

    build_investigation_recommendations(
        story,
        report,
    )

    build_investigation_allocator(
        story,
        report,
    )

    build_institutional_verdict(
        story,
        report,
        verification_url,
    )

    #
    # APPENDIX
    #

    build_investigation_appendix(
        story,
        report,
    )

    doc.build(

        story,

        onFirstPage=lambda canvas, doc: (
            draw_watermark(canvas)
        ),

        onLaterPages=_draw_header_footer,

    )

    pdf = buffer.getvalue()

    buffer.close()

    return pdf