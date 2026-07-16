from __future__ import annotations

from typing import Any

from app.services.investigations.models import InvestigationReport

from app.services.pdf.common.institutional_sections import (
    build_section_title,
    build_narrative,
)

from app.services.pdf.common.institutional_tables import (
    build_key_value_table,
)


def _value(value) -> str:
    if value is None:
        return "Not Available"

    if hasattr(value, "value"):
        value = value.value

    return str(value).replace("_", " ").title()


def build_executive_summary(
    story: list[Any],
    report: InvestigationReport,
) -> None:

    allocator = report.allocator
    summary = report.summary

    story.extend(
        build_section_title(
            "Executive Summary",
        )
    )

    story.extend(
        build_narrative(
            [
                summary.executive_summary,
            ]
        )
    )

    story.extend(
        build_section_title(
            "Institutional Metrics",
        )
    )

    story.append(
        build_key_value_table(
            {
                "Decision": _value(allocator.decision),
                "Confidence": f"{allocator.confidence:.2f}%",
                "Residual Risk": _value(allocator.residual_risk),
                "Critical Findings": str(summary.critical_findings),
                "Total Findings": str(summary.total_findings),
            }
        )
    )

    findings = report.findings[:3]

    if findings:

        story.extend(
            build_section_title(
                "Highest Priority Findings",
            )
        )

        story.extend(
            build_narrative(
                [
                    *[
                        f"• {finding.title}"
                        for finding in findings
                    ]
                ]
            )
        )