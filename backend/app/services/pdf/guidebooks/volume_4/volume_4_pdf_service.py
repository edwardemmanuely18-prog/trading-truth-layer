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
# VOLUME IV CONSTANTS
# ==========================================================

VOLUME_4_TITLE = (
    "Institutional Capital Allocation Infrastructure"
)

VOLUME_4_SUBTITLE = (
    "Institutional Trust Infrastructure for "
    "Evidence-Based Capital Allocation"
)

# ==========================================================
# VOLUME IV COMPONENTS
# ==========================================================

from app.services.pdf.guidebooks.volume_4.table_of_contents import (
    build_table_of_contents,
)

from app.services.pdf.guidebooks.volume_4.introduction import (
    build_introduction,
)

from app.services.pdf.guidebooks.volume_4.documentation_methodology import (
    build_documentation_methodology,
)

from app.services.pdf.guidebooks.volume_4.ttl_domains import (
    build_ttl_domains,
)

from app.services.pdf.guidebooks.volume_4.domain_1_dashboard import (
    build_domain_1_dashboard,
)

from app.services.pdf.guidebooks.volume_4.domain_2_evidence_intake import (
    build_domain_2_evidence_intake,
)

from app.services.pdf.guidebooks.volume_4.domain_3_evidence_registry import (
    build_domain_3_evidence_registry,
)

from app.services.pdf.guidebooks.volume_4.domain_4_claim_operations import (
    build_domain_4_claim_operations,
)

from app.services.pdf.guidebooks.volume_4.domain_5_trust_intelligence import (
    build_domain_5_trust_intelligence,
)

from app.services.pdf.guidebooks.volume_4.domain_6_investigation_center import (
    build_domain_6_investigation_center,
)

from app.services.pdf.guidebooks.volume_4.domain_7_public_trust_layer import (
    build_domain_7_public_trust_layer,
)

from app.services.pdf.guidebooks.volume_4.domain_8_administration import (
    build_domain_8_administration,
)

from app.services.pdf.guidebooks.volume_4.conclusion import (
    build_conclusion,
)

from app.services.pdf.guidebooks.volume_4.next_volume import (
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
        title="VOLUME IV",
        subtitle=VOLUME_4_TITLE,
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
            volume_number=4,
            title=VOLUME_4_TITLE,
            subtitle=VOLUME_4_SUBTITLE,
            publication_type=GUIDEBOOK_PUBLICATION_TYPE,
        )
    )

    # --------------------------------------------------
    # TABLE OF CONTENTS
    # --------------------------------------------------

    story.extend(
        build_table_of_contents()
    )

    # --------------------------------------------------
    # INTRODUCTION
    # --------------------------------------------------

    story.extend(
        build_introduction()
    )

    # --------------------------------------------------
    # DOCUMENTATION METHODOLOGY
    # --------------------------------------------------

    story.extend(
        build_documentation_methodology()
    )

    # --------------------------------------------------
    # TTL DOMAINS
    # --------------------------------------------------

    story.extend(
        build_ttl_domains()
    )

    # --------------------------------------------------
    # DOMAIN I
    # --------------------------------------------------

    story.extend(
        build_domain_1_dashboard()
    )

    # --------------------------------------------------
    # DOMAIN II
    # --------------------------------------------------

    story.extend(
        build_domain_2_evidence_intake()
    )

    # --------------------------------------------------
    # DOMAIN III
    # --------------------------------------------------

    story.extend(
        build_domain_3_evidence_registry()
    )

    # --------------------------------------------------
    # DOMAIN IV
    # --------------------------------------------------

    story.extend(
        build_domain_4_claim_operations()
    )

    # --------------------------------------------------
    # DOMAIN V
    # --------------------------------------------------

    story.extend(
        build_domain_5_trust_intelligence()
    )

    # --------------------------------------------------
    # DOMAIN VI
    # --------------------------------------------------

    story.extend(
        build_domain_6_investigation_center()
    )

    # --------------------------------------------------
    # DOMAIN VII
    # --------------------------------------------------

    story.extend(
        build_domain_7_public_trust_layer()
    )

    # --------------------------------------------------
    # DOMAIN VIII
    # --------------------------------------------------

    story.extend(
        build_domain_8_administration()
    )

    # --------------------------------------------------
    # CONCLUSION
    # --------------------------------------------------

    story.extend(
        build_conclusion()
    )

    # --------------------------------------------------
    # NEXT VOLUME PREVIEW
    # --------------------------------------------------

    story.extend(
        build_next_volume()
    )

    return story


# ==========================================================
# PUBLIC API
# ==========================================================


def generate_volume_4_pdf():

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
        title="Trading Truth Layer Guidebook Volume IV",
        author="Trading Truth Layer",
        subject=VOLUME_4_TITLE,
    )

    story = _build_story()

    doc.build(
        story,
        onFirstPage=_decorate_page,
        onLaterPages=_decorate_page,
    )

    buffer.seek(0)

    filename = (
        "ttl_guidebook_volume_4.pdf"
    )

    return (
        buffer,
        filename,
    )