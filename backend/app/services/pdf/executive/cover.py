from __future__ import annotations

from typing import Any

from app.services.investigations.models import (
    InvestigationReport,
)

from app.services.pdf.common.institutional_cover import (
    build_institutional_cover,
)

from app.services.pdf.common.institutional_tables import (
    build_key_value_table,
)

from app.services.pdf.common.institutional_sections import (
    build_narrative,
)


# ==========================================================
# Executive Cover
# ==========================================================


def _value(value) -> str:

    if value is None:
        return "Not Available"

    if hasattr(value, "value"):
        value = value.value

    return str(value).replace("_", " ").title()


# ==========================================================
# Cover
# ==========================================================


def build_executive_cover(
    story: list[Any],
    report: InvestigationReport,
    verification_url: str,
) -> None:
    """
    Page One

    Institutional executive briefing.

    Intended for CIOs,
    Investment Committees,
    Allocators,
    Regulators.

    Everything on this page should be readable
    in under sixty seconds.
    """

    allocator = report.allocator
    summary = report.summary

    confidence = 0.0

    if report.summary:
        confidence = report.summary.investigation_confidence

    band = (
        _value(allocator.decision)
        if allocator
        else "Executive Report"
    )

    metadata = {

        "Investigation Engine":
            "Institutional Investigation System (IIS)",

        "Workspace ID":
            str(report.workspace_id),

        "Generated":
            str(report.generated_at),

        "Status":
            _value(report.status),

        "Verification URL":
            verification_url,

    }

    story.extend(

        build_institutional_cover(

            title="Executive Investigation Report",

            subtitle="Institutional Investigation System (IIS)",

            score=confidence,

            band=band,

            metadata=metadata,

            classification=(

                "Trading Truth Layer Confidential "
                "Executive Investigation Report"

            ),

            notice=(

                "This executive briefing summarizes the "
                "institutional outcome of the completed "
                "investigation. Full forensic evidence is "
                "available within the Institutional "
                "Investigation Report."

            ),

        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "This executive report provides the official "
                    "institutional outcome of the completed "
                    "investigation. Detailed forensic evidence is "
                    "available within the Institutional Investigation "
                    "Report."
                ),

            ]

        )

    )
