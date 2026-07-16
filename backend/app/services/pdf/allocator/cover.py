from __future__ import annotations

from datetime import datetime

from app.services.pdf.common.institutional_cover import (
    build_institutional_cover,
)


# ==========================================================
# ALLOCATOR COVER
# ==========================================================

def build_cover_page(
    report,
    workspace_id: int,
    report_hash: str,
    verification_url: str,
):
    """
    Allocator Report Cover Adapter.

    This module intentionally contains no layout
    logic.

    It adapts the allocator payload into the
    canonical institutional cover framework.

    The common framework owns all typography,
    spacing, metadata layout and visual design.
    """

    allocator = report["allocator_assessment"]

    certificate = report.get(
        "verification_certificate"
    )

    #
    # Canonical TVS values
    #

    verification_score = (
        getattr(
            certificate,
            "average_verification_score",
            None,
        )
        if certificate
        else None
    )

    verification_band = (
        getattr(
            certificate,
            "verification_band",
            None,
        )
        if certificate
        else None
    )

    #
    # Compatibility fallback
    #

    if verification_score is None:

        verification_score = report.get(
            "verification",
            {},
        ).get(
            "verification_score",
            allocator.get(
                "allocator_score",
                0,
            ),
        )

    if verification_band is None:

        verification_band = report.get(
            "verification",
            {},
        ).get(
            "verification_band",
            allocator.get(
                "allocator_band",
                "-",
            ),
        )

    #
    # Institutional metadata
    #

    metadata = {

        "Workspace":
            f"Workspace {workspace_id}",

        "Generated":
            datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M UTC"
            ),

        "TVS Version":
            report.get(
                "report_metadata",
                {},
            ).get(
                "version",
                "2.0",
            ),

        "Report Hash":
            report_hash,

        "Verification Engine":
            report.get(
                "report_metadata",
                {},
            ).get(
                "verification_engine",
                "TVS",
            ),

        "Verification URL":

            verification_url,

    }

    return build_institutional_cover(

        title=
            "Allocator Due Diligence Report",

        subtitle=
            "Institutional Capital Allocation Assessment",

        score=
            f"{verification_score:.2f}",

        band=
            verification_band,

        metadata=
            metadata,

        classification=
            "Confidential Institutional Document",

        notice=(
            "Generated using the Trading Truth Layer "
            "Trading Verification System (TVS). "
            "This report is intended to support "
            "institutional capital allocation and "
            "due diligence decisions."
        ),

    )