from __future__ import annotations

import hashlib
import json

from io import BytesIO

from datetime import datetime, UTC

from reportlab.platypus import (
    SimpleDocTemplate,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    PAGE_MARGIN,
    PAGE_WIDTH,
    PAGE_HEIGHT,
)

from app.services.pdf.common.institutional_header_footer import (
    draw_header,
    draw_footer,
)

from app.services.pdf.common.institutional_watermark import (
    draw_watermark,
)

from app.services.pdf.common.institutional_qr import (
    build_qr,
)

from app.services.pdf.claim_report.context import (
    build_claim_report_context,
)

from app.services.pdf.claim_report.cover import (
    build_cover,
)

from app.services.pdf.claim_report.executive_summary import (
    build_executive_summary,
)

from app.services.pdf.claim_report.performance import (
    build_performance_section,
)

from app.services.pdf.claim_report.verification import (
    build_verification_section,
)

from app.services.pdf.claim_report.governance import (
    build_governance_section,
)

from app.services.pdf.claim_report.evidence import (
    build_evidence_section,
)

from app.services.pdf.claim_report.audit import (
    build_audit_section,
)

from app.services.pdf.claim_report.verdict import (
    build_verdict_section,
)


# ==========================================================
# DOCUMENT CALLBACK
# ==========================================================

def _decorate_page(
    canvas,
    doc,
    *,
    report_hash: str,
    report_title: str,
):

    draw_watermark(
        canvas,
    )

    draw_header(
        canvas,
        title=report_title,
        subtitle="Institutional Claim Report",
        tvs_version="TVS Canonical",
    )

    draw_footer(
        canvas,
        doc,
        report_hash=report_hash,
    )

# ==========================================================
# STORY BUILDER
# ==========================================================

def _build_story(
    context: dict,
    *,
    report_hash: str,
    verification_url: str | None,
):
    """
    Builds the institutional Claim Report in the
    same narrative progression used throughout
    Trading Truth Layer.

    The report is intentionally organized as an
    institutional due diligence investigation.

    Narrative Flow

        Cover
            ↓
        Executive Assessment
            ↓
        Trading Performance (TPS)
            ↓
        Evidence Assessment
            ↓
        Trading Verification Assessment (TVS)
            ↓
        Operational Governance
            ↓
        Audit & Verification Lineage
            ↓
        Institutional Verdict
    """

    story = []

    # ======================================================
    # Cover
    # ======================================================

    story.extend(
        build_cover(
            context,
        )
    )

    story.append(PageBreak())

    #
    # Executive Summary
    #

    story.extend(
        build_executive_summary(
            context,
        )
    )

    story.append(
        PageBreak()
    )

    #
    # Trading Performance
    #

    story.extend(
        build_performance_section(
            context,
        )
    )

    # ======================================================
    # Evidence Assessment
    # ======================================================

    story.extend(
        build_evidence_section(
            context,
        )
    )

    # ======================================================
    # Trading Verification Assessment (TVS)
    # ======================================================

    story.extend(
        build_verification_section(
            context,
        )
    )

    # ======================================================
    # Operational Governance
    # ======================================================

    story.extend(
        build_governance_section(
            context,
        )
    )

    # ======================================================
    # Audit & Verification Lineage
    # ======================================================

    story.extend(
        build_audit_section(
            context,
        )
    )

    # ======================================================
    # Institutional Verdict
    # ======================================================

    story.extend(

        build_verdict_section(

            context,

            report_hash=report_hash,

            verification_url=verification_url,

        )

    )

    return story

# ==========================================================
# PDF BUILDER
# ==========================================================

def generate_claim_report_pdf(
    *,
    db,
    schema,
    verification_url: str | None = None,
):
    """
    Generates the institutional Claim Report PDF.

    All verification metrics originate from the
    canonical Trading Verification System (TVS).

    This function performs no verification logic.
    """

    #
    # ------------------------------------------------------
    # Canonical Context
    # ------------------------------------------------------
    #

    context = build_claim_report_context(
        schema=schema,
        db=db,
    )

    #
    # Canonical verification URL
    #

    verification_url = (
        verification_url
        or context["metadata"].get("verification_url")
    )

    #
    # Older certificates may still expose /public/verify/.
    # Convert every legacy URL to the canonical Verify endpoint.
    #

    if verification_url:

        verification_url = verification_url.replace(
            "/public/verify/",
            "/verify/",
        )

        if verification_url.startswith("/"):

            verification_url = (
                "https://www.tradingtruthlayer.com"
                + verification_url
            )

    context["metadata"]["verification_url"] = verification_url

    #
    # ------------------------------------------------------
    # Verification QR
    # ------------------------------------------------------
    #

    qr = build_qr(
        verification_url or ""
    )

    context["qr_image"] = qr

    #
    # ------------------------------------------------------
    # Report Hash
    # ------------------------------------------------------
    #

    report_hash = hashlib.sha256(
        json.dumps(
            {
                "claim_id":
                    context["claim"]["id"],

                "claim_hash":
                    context["metadata"]["claim_hash"],

                "certificate_hash":
                    context["metadata"]["certificate_hash"],

                "verification_score":
                    context["verification"].verification_score,

                "verification_band":
                    context["verification"].verification_band,

                "verification_tier":
                    context["verification"].verification_tier,
            },
            sort_keys=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest()


    context["report"] = {

        "hash":
            report_hash,

        "title":
            "Institutional Claim Report",

        "subtitle":
            "Trading Verification System",

        "generator":
            "Trading Truth Layer",

        "generated":
            None,

        "schema_name":
            schema.name,

        "claim_id":
            schema.id,

        "workspace":
            context["metadata"].get(
                "workspace_name",
            ),

    }

    #
    # ------------------------------------------------------
    # Story
    # ------------------------------------------------------
    #

    story = _build_story(
        context,
        report_hash=report_hash,
        verification_url=verification_url,
    )

    #
    # ------------------------------------------------------
    # PDF Buffer
    # ------------------------------------------------------
    #

    buffer = BytesIO()

    doc = SimpleDocTemplate(

        buffer,

        pagesize=(

            PAGE_WIDTH,

            PAGE_HEIGHT,

        ),

        leftMargin=PAGE_MARGIN,

        rightMargin=PAGE_MARGIN,

        topMargin=PAGE_MARGIN + 42,

        bottomMargin=PAGE_MARGIN,

        title=f"Claim Report - {schema.name}",

        author="Trading Truth Layer",

        subject=(
            "Trading Truth Layer "
            "Institutional Verification Report"
        ),

    )

    #
    # ------------------------------------------------------
    # Page Decoration
    # ------------------------------------------------------
    #

    def decorate(canvas, document):

        _decorate_page(

            canvas,

            document,

            report_hash=report_hash,

            report_title=context["report"]["title"],

        )

    #
    # ------------------------------------------------------
    # Build
    # ------------------------------------------------------
    #

    doc.build(

        story,

        onFirstPage=decorate,

        onLaterPages=decorate,

    )

    context["report"]["generated"] = (
        datetime.now(UTC).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
    )

    buffer.seek(0)

    filename = (

        f"claim_report_{schema.id}.pdf"

    )

    return (

        buffer,

        filename,

    )

# ==========================================================
# PUBLIC ENTRY POINT
# ==========================================================

def build_claim_report_pdf(
    *,
    db,
    schema,
    verification_url: str | None = None,
):
    """
    Compatibility wrapper.

    Existing routes should continue calling this
    function while the Claim Report migrates to
    the institutional PDF framework.
    """

    return generate_claim_report_pdf(

        db=db,

        schema=schema,

        verification_url=verification_url,

    )