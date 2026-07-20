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

from app.services.pdf.guidebooks.common.next_volume_preview import (
    build_next_volume_preview,
)

# ==========================================================
# VOLUME II CONSTANTS
# ==========================================================

VOLUME_2_TITLE = (
    "Institutional Verification Infrastructure"
)

VOLUME_2_SUBTITLE = (
    "Independent Verification for "
    "Evidence-Based Capital Allocation"
)

# ==========================================================
# INTRODUCTION
# ==========================================================

from app.services.pdf.guidebooks.volume_2.introduction import (
    build_introduction,
)

# ==========================================================
# PART I
# ==========================================================

from app.services.pdf.guidebooks.volume_2.part_1.verification_problem import (
    build_verification_problem,
)

from app.services.pdf.guidebooks.volume_2.part_1.why_verification_matters import (
    build_why_verification_matters,
)

from app.services.pdf.guidebooks.volume_2.part_1.institutional_verification_thesis import (
    build_institutional_verification_thesis,
)

# ==========================================================
# PART II
# ==========================================================

from app.services.pdf.guidebooks.volume_2.part_2.what_is_verification_infrastructure import (
    build_what_is_verification_infrastructure,
)

from app.services.pdf.guidebooks.volume_2.part_2.the_verification_stack import (
    build_the_verification_stack,
)

from app.services.pdf.guidebooks.volume_2.part_2.verification_layers import (
    build_verification_layers,
)

# ==========================================================
# PART III
# ==========================================================

from app.services.pdf.guidebooks.volume_2.part_3.evidence_ingestion_engine import (
    build_evidence_ingestion_engine,
)

from app.services.pdf.guidebooks.volume_2.part_3.canonical_trade_ledger_engine import (
    build_canonical_trade_ledger_engine,
)

from app.services.pdf.guidebooks.volume_2.part_3.verification_engine import (
    build_verification_engine,
)

from app.services.pdf.guidebooks.volume_2.part_3.integrity_engine import (
    build_integrity_engine,
)

from app.services.pdf.guidebooks.volume_2.part_3.governance_engine import (
    build_governance_engine,
)

# ==========================================================
# PART IV
# ==========================================================

from app.services.pdf.guidebooks.volume_2.part_4.verification_workflow import (
    build_verification_workflow,
)

from app.services.pdf.guidebooks.volume_2.part_4.claim_lifecycle_workflow import (
    build_claim_lifecycle_workflow,
)

from app.services.pdf.guidebooks.volume_2.part_4.institutional_verification_workflow import (
    build_institutional_verification_workflow,
)

# ==========================================================
# PART V
# ==========================================================

from app.services.pdf.guidebooks.volume_2.part_5.institutional_outputs import (
    build_institutional_outputs,
)

from app.services.pdf.guidebooks.volume_2.part_5.verification_certificates import (
    build_verification_certificates,
)

from app.services.pdf.guidebooks.volume_2.part_5.evidence_packages import (
    build_evidence_packages,
)

# ==========================================================
# PART VI
# ==========================================================

from app.services.pdf.guidebooks.volume_2.part_6.the_future_of_verification import (
    build_the_future_of_verification,
)

from app.services.pdf.guidebooks.volume_2.part_6.conclusion import (
    build_conclusion,
)


def _decorate_page(canvas, doc):

    if canvas.getPageNumber() == 1:
        return

    draw_watermark(canvas)

    draw_header(
        canvas=canvas,
        title="VOLUME II",
        subtitle=VOLUME_2_TITLE,
        tvs_version=f"Guidebook Series v{GUIDEBOOK_SERIES_VERSION}",
    )

    draw_footer(
        canvas=canvas,
        doc=doc,
    )


def _build_story():

    story = []

    # --------------------------------------------------
    # COVER
    # --------------------------------------------------

    story.extend(
        build_guidebook_cover(
            volume_number=2,
            title=VOLUME_2_TITLE,
            subtitle=VOLUME_2_SUBTITLE,
            publication_type=GUIDEBOOK_PUBLICATION_TYPE,
        )
    )

    # --------------------------------------------------
    # INTRODUCTION
    # --------------------------------------------------

    story.extend(build_introduction())

    # --------------------------------------------------
    # PART I
    # --------------------------------------------------

    story.extend(build_verification_problem())
    story.extend(build_why_verification_matters())
    story.extend(
        build_institutional_verification_thesis()
    )

    # --------------------------------------------------
    # PART II
    # --------------------------------------------------

    story.extend(
        build_what_is_verification_infrastructure()
    )

    story.extend(
        build_the_verification_stack()
    )

    story.extend(
        build_verification_layers()
    )

    # --------------------------------------------------
    # PART III
    # --------------------------------------------------

    story.extend(
        build_evidence_ingestion_engine()
    )

    story.extend(
        build_canonical_trade_ledger_engine()
    )

    story.extend(
        build_verification_engine()
    )

    story.extend(
        build_integrity_engine()
    )

    story.extend(
        build_governance_engine()
    )

    # --------------------------------------------------
    # PART IV
    # --------------------------------------------------

    story.extend(
        build_verification_workflow()
    )

    story.extend(
        build_claim_lifecycle_workflow()
    )

    story.extend(
        build_institutional_verification_workflow()
    )

    # --------------------------------------------------
    # PART V
    # --------------------------------------------------

    story.extend(
        build_institutional_outputs()
    )

    story.extend(
        build_verification_certificates()
    )

    story.extend(
        build_evidence_packages()
    )

    # --------------------------------------------------
    # PART VI
    # --------------------------------------------------

    story.extend(
        build_the_future_of_verification()
    )

    story.extend(
        build_conclusion()
    )

    # --------------------------------------------------
    # NEXT VOLUME
    # --------------------------------------------------

    story.extend(
        build_next_volume_preview(
            current_volume=2,
        )
    )

    return story


def generate_volume_2_pdf():

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
        title="Trading Truth Layer Guidebook Volume II",
        author="Trading Truth Layer",
        subject=VOLUME_2_TITLE,
    )

    story = _build_story()

    doc.build(
        story,
        onFirstPage=_decorate_page,
        onLaterPages=_decorate_page,
    )

    buffer.seek(0)

    filename = (
        "ttl_guidebook_volume_2.pdf"
    )

    return (
        buffer,
        filename,
    )