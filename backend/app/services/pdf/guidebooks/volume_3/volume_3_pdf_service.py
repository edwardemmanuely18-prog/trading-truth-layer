from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
)

# ==========================================================
# INSTITUTIONAL PDF INFRASTRUCTURE
# ==========================================================

from app.services.pdf.common.institutional_theme import (
    PAGE_WIDTH,
    PAGE_HEIGHT,
    PAGE_MARGIN,
)

# ==========================================================
# GUIDEBOOK PDF MARGINS
# ==========================================================

GUIDEBOOK_TOP_MARGIN = PAGE_MARGIN + 65

GUIDEBOOK_BOTTOM_MARGIN = PAGE_MARGIN + 25


from app.services.pdf.common.institutional_header_footer import (
    draw_header,
    draw_footer,
)

from app.services.pdf.common.institutional_watermark import (
    draw_watermark,
)

# ==========================================================
# GUIDEBOOK CONSTANTS
# ==========================================================

from app.services.pdf.guidebooks.common.guidebook_constants import (
    GUIDEBOOK_SERIES_VERSION,
    GUIDEBOOK_PUBLICATION_TYPE,
)

# ==========================================================
# COMMON COMPONENTS
# ==========================================================

from app.services.pdf.guidebooks.common.guidebook_cover import (
    build_guidebook_cover,
)

# ==========================================================
# VOLUME III CONSTANTS
# ==========================================================

VOLUME_3_TITLE = (
    "Trading Verification Infrastructure"
)

VOLUME_3_SUBTITLE = (
    "Independent Trading Verification for "
    "Evidence-Based Capital Allocation"
)

# ==========================================================
# VOLUME III COMPONENTS
# ==========================================================

from app.services.pdf.guidebooks.volume_3.cover import (
    build_cover,
)

from app.services.pdf.guidebooks.volume_3.introduction import (
    build_introduction,
)

from app.services.pdf.guidebooks.volume_3.verification_problem import (
    build_verification_problem,
)

from app.services.pdf.guidebooks.volume_3.verification_thesis import (
    build_verification_thesis,
)

from app.services.pdf.guidebooks.volume_3.what_is_trading_verification import (
    build_what_is_trading_verification,
)

from app.services.pdf.guidebooks.volume_3.sync_center import (
    build_sync_center,
)

from app.services.pdf.guidebooks.volume_3.evidence_acquisition import (
    build_evidence_acquisition,
)

from app.services.pdf.guidebooks.volume_3.institutional_standards import (
    build_institutional_standards,
)

from app.services.pdf.guidebooks.volume_3.verification_metrics import (
    build_verification_metrics,
)

from app.services.pdf.guidebooks.volume_3.verification_bands import (
    build_verification_bands,
)

from app.services.pdf.guidebooks.volume_3.verification_certificates import (
    build_verification_certificates,
)

from app.services.pdf.guidebooks.volume_3.institutional_outputs import (
    build_institutional_outputs,
)

from app.services.pdf.guidebooks.volume_3.verification_workflow import (
    build_verification_workflow,
)

from app.services.pdf.guidebooks.volume_3.future_of_trading_verification import (
    build_future_of_trading_verification,
)

from app.services.pdf.guidebooks.volume_3.conclusion import (
    build_conclusion,
)

from app.services.pdf.guidebooks.volume_3.next_volume import (
    build_next_volume,
)


# ==========================================================
# PAGE DECORATION
# ==========================================================


def _decorate_page(canvas, doc):

    if canvas.getPageNumber() == 1:
        return

    draw_watermark(canvas)

    draw_header(
        canvas=canvas,
        title="VOLUME III",
        subtitle=VOLUME_3_TITLE,
        tvs_version=f"Guidebook Series v{GUIDEBOOK_SERIES_VERSION}",
    )

    draw_footer(
        canvas=canvas,
        doc=doc,
    )


# ==========================================================
# STORY BUILDER
# ==========================================================


def _build_story():

    story = []

    # --------------------------------------------------
    # COVER
    # --------------------------------------------------

    story.extend(
        build_guidebook_cover(
            volume_number=3,
            title=VOLUME_3_TITLE,
            subtitle=VOLUME_3_SUBTITLE,
            publication_type=GUIDEBOOK_PUBLICATION_TYPE,
        )
    )

    # --------------------------------------------------
    # CONTENTS
    # --------------------------------------------------

    story.extend(build_introduction())
    story.extend(build_verification_problem())
    story.extend(build_verification_thesis())
    story.extend(
        build_what_is_trading_verification()
    )
    story.extend(
        build_sync_center()
    )
    story.extend(
        build_evidence_acquisition()
    )
    story.extend(
        build_institutional_standards()
    )
    story.extend(
        build_verification_metrics()
    )
    story.extend(
        build_verification_bands()
    )
    story.extend(
        build_verification_certificates()
    )
    story.extend(
        build_institutional_outputs()
    )
    story.extend(
        build_verification_workflow()
    )
    story.extend(
        build_future_of_trading_verification()
    )
    story.extend(
        build_conclusion()
    )
    story.extend(
        build_next_volume()
    )

    return story


# ==========================================================
# PUBLIC API
# ==========================================================


def generate_volume_3_pdf():

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(
            PAGE_WIDTH,
            PAGE_HEIGHT,
        ),
        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,
        topMargin=GUIDEBOOK_TOP_MARGIN,
        bottomMargin=GUIDEBOOK_BOTTOM_MARGIN,
        title="Trading Truth Layer Guidebook Volume III",
        author="Trading Truth Layer",
        subject=VOLUME_3_TITLE,
    )

    story = _build_story()

    doc.build(
        story,
        onFirstPage=_decorate_page,
        onLaterPages=_decorate_page,
    )

    buffer.seek(0)

    filename = (
        "ttl_guidebook_volume_3.pdf"
    )

    return (
        buffer,
        filename,
    )