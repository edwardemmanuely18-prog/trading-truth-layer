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
    draw_header,
    draw_footer,
)

from app.services.pdf.common.institutional_watermark import (
    draw_watermark,
    draw_verified_stamp,
)

from app.services.pdf.common.institutional_theme import (
    PAGE_MARGIN,
    TOP_MARGIN,
    BOTTOM_MARGIN,
    FOOTER_HEIGHT,
)

from .cover import build_executive_cover
from .summary import build_executive_summary
from .decision import build_executive_decision


# ==========================================================
# Header / Footer
# ==========================================================

def _draw_header_footer(canvas, doc):

    draw_watermark(canvas)

    draw_header(
        canvas,
        title="Executive Investigation Report",
        subtitle="Institutional Investigation System",
        tvs_version="IIS Executive",
    )

    draw_footer(
        canvas,
        doc,
        report_hash="",
    )

    draw_verified_stamp(canvas)


# ==========================================================
# Generator
# ==========================================================

def generate_executive_report_pdf(
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

    story: list = []

    build_executive_cover(
        story,
        report,
        verification_url,
    )

    story.append(PageBreak())

    build_executive_summary(
        story,
        report,
    )

    story.append(PageBreak())

    build_executive_decision(
        story,
        report,
        verification_url,
    )

    doc.build(
        story,
        onFirstPage=lambda canvas, doc: draw_watermark(canvas),
        onLaterPages=_draw_header_footer,
    )

    pdf = buffer.getvalue()

    buffer.close()

    return pdf