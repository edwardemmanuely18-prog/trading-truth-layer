from __future__ import annotations

from typing import Any

from app.services.investigations.models import (
    InvestigationReport,
)

from app.services.pdf.common.institutional_cover import (
    build_institutional_cover,
)


# ==========================================================
# Helpers
# ==========================================================

def _label(value) -> str:

    if value is None:
        return "Unavailable"

    return (
        str(value)
        .replace("_", " ")
        .title()
    )


# ==========================================================
# Investigation Cover
# ==========================================================


def build_investigation_cover(
    story: list[Any],
    report: InvestigationReport,
    verification_url: str,
) -> None:
    """
    Investigation Report cover.

    Uses the existing institutional cover framework.
    """

    confidence = 0.0

    if report.summary:
        confidence = report.summary.investigation_confidence

    allocator = report.allocator

    band = (
        _label(allocator.decision)
        if allocator is not None
        else "Investigation"
    )

    metadata = {
        "Investigation Engine": "Institutional Investigation System (IIS)",
        "Workspace ID": str(report.workspace_id),
        "Generated": str(report.generated_at),
        "Status": _label(report.status.value),
        "Verification URL": verification_url,
    }

    story.extend(

        build_institutional_cover(

            title="Institutional Investigation Report",

            subtitle="Institutional Investigation System (IIS)",

            score=confidence,

            band=band,

            metadata=metadata,

            classification=(
                "Trading Truth Layer Confidential "
                "Institutional Investigation Report"
            ),

            notice=(
                "This report reconstructs the complete institutional "
                "investigation performed by the Institutional "
                "Investigation System (IIS). Every conclusion is "
                "derived from the canonical Investigation Context "
                "and remains independently reproducible."
            ),

        )

    )