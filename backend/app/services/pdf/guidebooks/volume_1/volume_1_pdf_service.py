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
    VOLUME_1_TITLE,
    GUIDEBOOK_SERIES_VERSION,
    GUIDEBOOK_PUBLICATION_TYPE,
    TTL_SHORT_POSITIONING_STATEMENT,
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
# VOLUME I
# ==========================================================

from app.services.pdf.guidebooks.volume_1.four_questions import (
    build_four_questions,
)

from app.services.pdf.guidebooks.volume_1.introduction import (
    build_introduction,
)

from app.services.pdf.guidebooks.volume_1.the_missing_institutional_infrastructure import (
    build_missing_institutional_infrastructure,
)

from app.services.pdf.guidebooks.volume_1.why_trust_infrastructure_matters import (
    build_why_trust_infrastructure_matters,
)

from app.services.pdf.guidebooks.volume_1.part_6.conclusion import (
    build_conclusion,
)

# ==========================================================
# PART I
# ==========================================================

from app.services.pdf.guidebooks.volume_1.part_1.trust_problem import (
    build_part_1,
)

from app.services.pdf.guidebooks.volume_1.part_1.global_trading_trust_problem import (
    build_global_trading_trust_problem,
)

from app.services.pdf.guidebooks.volume_1.part_1.capital_allocation_problem import (
    build_capital_allocation_problem,
)

from app.services.pdf.guidebooks.volume_1.part_1.institutional_due_diligence_problem import (
    build_institutional_due_diligence_problem,
)

# ==========================================================
# PART II
# ==========================================================

from app.services.pdf.guidebooks.volume_1.part_2.missing_infrastructure import (
    build_missing_infrastructure,
)

# ==========================================================
# PART III
# ==========================================================

from app.services.pdf.guidebooks.volume_1.part_3.what_is_ttl import (
    build_what_is_ttl,
)

from app.services.pdf.guidebooks.volume_1.part_3.who_is_ttl_built_for import (
    build_who_is_ttl_built_for,
)

from app.services.pdf.guidebooks.volume_1.part_3.five_problems_ttl_solves import (
    build_five_problems_ttl_addresses,
)

# ==========================================================
# PART IV
# ==========================================================

from app.services.pdf.guidebooks.volume_1.part_4.from_performance_to_trust import (
    build_from_performance_to_trust,
)

from app.services.pdf.guidebooks.volume_1.part_4.the_institutional_realization import (
    build_institutional_realization,
)

from app.services.pdf.guidebooks.volume_1.part_4.trading_trust_infrastructure_thesis import (
    build_trading_trust_infrastructure_thesis,
)

from app.services.pdf.guidebooks.volume_1.part_4.institutional_positioning import (
    build_institutional_positioning,
)

# ==========================================================
# PART V
# ==========================================================

from app.services.pdf.guidebooks.volume_1.part_5.ttl_doctrine import (
    build_ttl_doctrine,
)

from app.services.pdf.guidebooks.volume_1.part_4.evolution_of_capital_allocation import (
    build_evolution_of_capital_allocation,
)



def _decorate_page(canvas, doc):

    if canvas.getPageNumber() == 1:
        return

    draw_watermark(canvas)

    draw_header(
        canvas=canvas,
        title="VOLUME I",
        subtitle=VOLUME_1_TITLE,
        tvs_version=f"Guidebook Series v{GUIDEBOOK_SERIES_VERSION}",
    )

    draw_footer(
        canvas=canvas,
        doc=doc,
    )

def _build_story():

    story = []

    # COVER

    story.extend(
        build_guidebook_cover(
            volume_number=1,
            title=VOLUME_1_TITLE,
            subtitle=TTL_SHORT_POSITIONING_STATEMENT,
            publication_type=GUIDEBOOK_PUBLICATION_TYPE,
        )
    )

    # VOLUME I

    story.extend(build_four_questions())

    story.extend(
        build_introduction()
    )

    story.extend(
        build_missing_institutional_infrastructure()
    )

    story.extend(
        build_why_trust_infrastructure_matters()
    )

    # PART I

    story.extend(build_part_1())
    story.extend(build_global_trading_trust_problem())
    story.extend(build_capital_allocation_problem())
    story.extend(build_institutional_due_diligence_problem())

    # PART II

    story.extend(build_missing_infrastructure())

    # PART III

    story.extend(build_what_is_ttl())
    story.extend(build_who_is_ttl_built_for())
    story.extend(build_five_problems_ttl_addresses())

    # PART IV

    story.extend(
        build_from_performance_to_trust()
    )

    story.extend(
        build_institutional_realization()
    )

    story.extend(
        build_evolution_of_capital_allocation()
    )

    story.extend(
        build_trading_trust_infrastructure_thesis()
    )

    story.extend(
        build_institutional_positioning()
    )

    # PART V

    story.extend(build_ttl_doctrine())

    # CONCLUSION

    story.extend(build_conclusion())

    # NEXT VOLUME

    story.extend(
        build_next_volume_preview(
            current_volume=1,
        )
    )

    return story


def generate_volume_1_pdf():

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,
        topMargin=GUIDEBOOK_TOP_MARGIN,
        bottomMargin=GUIDEBOOK_BOTTOM_MARGIN,
        title="Trading Truth Layer Guidebook Volume I",
        author="Trading Truth Layer",
        subject=VOLUME_1_TITLE,
    )

    story = _build_story()

    doc.build(
        story,
        onFirstPage=_decorate_page,
        onLaterPages=_decorate_page,
    )

    buffer.seek(0)

    filename = "ttl_guidebook_volume_1.pdf"

    return (
        buffer,
        filename,
    )