from __future__ import annotations

from typing import Any

from reportlab.platypus import KeepTogether

from app.services.investigations.models import (
    InvestigationFinding,
    InvestigationReport,
)

from app.services.pdf.common.institutional_sections import (
    build_narrative,
    build_section_title,
)

from app.services.pdf.common.institutional_tables import (
    build_key_value_table,
)



# ==========================================================
# Helpers
# ==========================================================


def _severity(value) -> str:

    if hasattr(value, "value"):

        value = value.value

    return str(value).replace("_", " ").title()


def _confidence(value: float | None) -> str:

    if value is None:

        return "Not Available"

    return f"{value:.2f}%"


def _affected(finding: InvestigationFinding) -> str:

    parts = []

    if finding.affected_claims:
        parts.append(f"{len(finding.affected_claims)} Claim(s)")

    if finding.affected_trades:
        parts.append(f"{len(finding.affected_trades)} Trade(s)")

    if finding.affected_members:
        parts.append(f"{len(finding.affected_members)} Member(s)")

    if finding.affected_accounts:
        parts.append(f"{len(finding.affected_accounts)} Account(s)")

    if finding.affected_sync_jobs:
        parts.append(f"{len(finding.affected_sync_jobs)} Sync Job(s)")

    if not parts:
        return "None"

    return ", ".join(parts)


def _finding_card(
    story: list[Any],
    finding: InvestigationFinding,
) -> None:

    block = [

        build_key_value_table(

            {

                "Severity":
                    _severity(finding.severity),

                "Confidence":
                    _confidence(finding.confidence),

                "Affected Assets":
                    _affected(finding),

            }

        ),

        *build_narrative(

            [

                f"Finding: {finding.title}",

                finding.recommendation
                if finding.recommendation
                else "No remediation recommendation was provided."

            ]

        ),

    ]

    story.append(
        KeepTogether(block)
    )


# ==========================================================
# Findings
# ==========================================================


def build_investigation_findings(
    story: list[Any],
    report: InvestigationReport,
) -> None:

    story.extend(

        build_section_title(

            "Institutional Investigation Findings",

        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "This section consolidates the validated findings "
                    "produced by every analytical domain participating "
                    "in the Institutional Investigation System."
                ),

                (
                    "Each finding is independently traceable to the "
                    "canonical Investigation Context and contributes "
                    "directly to allocator reasoning."
                ),

            ]

        )

    )

    findings = report.findings or []

    if not findings:

        story.extend(

            build_narrative(

                [

                    (
                        "No investigation findings were generated "
                        "during this investigation."

                    )

                ]

            )

        )

        return

    for finding in findings:

        _finding_card(
            story,
            finding,
        )

    story.extend(

        build_narrative(

            [

                (

                    f"The Institutional Investigation System produced "

                    f"{len(findings)} validated finding(s)."

                ),

                (

                    "Each finding remains permanently traceable to its "

                    "supporting evidence, analytical domain and "

                    "allocator decision."

                ),

            ]

        )

    )