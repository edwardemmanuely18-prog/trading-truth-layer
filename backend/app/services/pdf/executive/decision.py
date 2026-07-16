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


def _value(value) -> str:
    if value is None:
        return "Not Available"

    if hasattr(value, "value"):
        value = value.value

    return str(value).replace("_", " ").title()


def build_executive_decision(
    story: list[Any],
    report: InvestigationReport,
    verification_url: str,
) -> None:

    allocator = report.allocator

    story.extend(
        build_section_title(
            "Institutional Decision",
        )
    )

    story.append(
        build_key_value_table(
            {
                "Decision": _value(allocator.decision),
                "Confidence": f"{allocator.confidence:.2f}%",
                "Residual Risk": _value(allocator.residual_risk),
                "Required Actions": str(
                    len(allocator.required_actions)
                ),
            }
        )
    )

    if allocator.rationale:

        story.extend(
            build_section_title(
                "Decision Rationale",
            )
        )

        story.extend(
            build_narrative(
                [
                    allocator.rationale,
                ]
            )
        )

    actions = [
        action
        for action in allocator.required_actions
        if action
    ]

    if actions:

        story.extend(
            build_section_title(
                "Required Actions",
            )
        )

        story.extend(
            build_narrative(
                [
                    *[
                        f"• {action}"
                        for action in actions
                    ]
                ]
            )
        )

    story.extend(
        build_section_title(
            "Executive Interpretation",
        )
    )

    story.extend(
        build_narrative(
            [
                (
                    "This report provides the official institutional "
                    "decision of the Investigation Intelligence System. "
                    "Detailed forensic reconstruction, analytical "
                    "evidence and investigation domains remain "
                    "available within the Institutional Investigation "
                    "Report."
                ),
            ]
        )
    )

    story.extend(
        build_section_title(
            "Verification",
        )
    )

    story.append(
        build_key_value_table(
            {
                "System": "Institutional Investigation System",
                "Verification": verification_url,
            }
        )
    )