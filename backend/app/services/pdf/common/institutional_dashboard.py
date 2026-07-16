from __future__ import annotations

"""
Trading Truth Layer
Institutional Executive Dashboard

Every institutional report begins with a standardized
executive dashboard.

This module builds the canonical dashboard used across:

• Claim Report
• Investigation Report
• Verification Report
• Allocator Report
• Due Diligence Report
• Audit Report
• Evidence Report
"""

from reportlab.platypus import Spacer

from .institutional_sections import (
    build_section_heading,
)

from .institutional_tables import (
    build_key_value_table,
)

from .institutional_registry import (
    InstitutionalReportDefinition,
)


# ==========================================================
# DASHBOARD
# ==========================================================

def build_dashboard(
    *,
    report: InstitutionalReportDefinition,
    score: float,
    decision: str,
    confidence: float,
    risk: str,
    generated: str,
    workspace: str,
    report_id: str,
    verification_band: str,
):
    """
    Canonical executive dashboard.

    Every institutional report should begin
    with this dashboard immediately after
    the cover page.
    """

    story = []

    story.extend(

        build_section_heading(

            "Executive Dashboard",

            (
                "Institutional executive overview generated "
                "from the canonical Trading Truth Layer "
                "verification infrastructure."
            ),

        )

    )

    story.append(

        build_key_value_table(

            {

                "Report":
                    report.title,

                "Classification":
                    report.classification,

                "System":
                    report.system,

                "Version":
                    report.version,

                "Workspace":
                    workspace,

                "Report ID":
                    report_id,

                "Overall Score":
                    f"{score:.2f}",

                "Decision":
                    decision,

                "Confidence":
                    f"{confidence:.2f}%",

                "Residual Risk":
                    risk,

                "Verification Band":
                    verification_band,

                "Generated":
                    generated,

            }

        )

    )

    story.append(
        Spacer(
            1,
            10,
        )
    )

    return story