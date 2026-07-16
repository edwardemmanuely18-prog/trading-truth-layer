from __future__ import annotations

from typing import Any

from app.services.investigations.models import (
    InvestigationReport,
)

from app.services.pdf.common.institutional_sections import (
    build_section_title,
    build_narrative,
)

from app.services.pdf.common.institutional_tables import (
    build_key_value_table,
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
# Executive Investigation Summary
# ==========================================================

def build_investigation_executive_summary(
    story: list[Any],
    report: InvestigationReport,
) -> None:
    """
    Executive summary of the institutional investigation.

    This section provides a concise executive briefing before
    the detailed forensic reconstruction begins.
    """

    summary = report.summary

    allocator = report.allocator

    story.extend(

        build_section_title(
            "Executive Investigation Summary",
        )

    )

    story.extend(

        build_narrative(

            [
                (
                    "The Institutional Investigation System (IIS) "
                    "reconstructed the complete investigation context "
                    "from the canonical Investigation Context."
                ),

                (
                    "Execution integrity, evidence provenance, "
                    "verification, governance, synchronization, "
                    "broker activity, behavioural consistency "
                    "and institutional review were independently "
                    "evaluated before producing the allocator decision."
                ),

                (
                    "Every conclusion contained in this report is "
                    "derived from canonical investigation evidence "
                    "and is fully reproducible."
                ),

            ]

        )

    )

    story.append(

        build_key_value_table(

            {

                "Investigation Confidence":
                    f"{summary.investigation_confidence:.2f}%",

                "Allocator Decision":
                    _label(
                        allocator.decision
                    )
                    if allocator
                    else "Unavailable",

                "Residual Risk":
                    _label(
                        allocator.residual_risk.value
                    )
                    if allocator
                    else "Unavailable",

                "Evidence Nodes":
                    str(summary.evidence_nodes),

                "Relationships":
                    str(summary.relationships),

                "Timeline Events":
                    str(summary.timeline_events),

                "Total Findings":
                    str(summary.total_findings),

                "Critical Findings":
                    str(summary.critical_findings),

            }

        )

    )

    story.extend(

        build_narrative(

            summary.executive_summary,

        )

    )