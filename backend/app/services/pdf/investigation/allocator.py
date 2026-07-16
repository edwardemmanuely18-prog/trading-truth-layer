from __future__ import annotations

from typing import Any

from reportlab.platypus import KeepTogether

from app.services.investigations.models import (
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


def _value(value) -> str:

    if value is None:
        return "Not Available"

    if hasattr(value, "value"):
        value = value.value

    text = str(value).strip()

    if text in (
        "",
        "Unknown",
        "None",
        "{}",
        "[]",
    ):
        return "Not Available"

    return text.replace("_", " ").title()


# ==========================================================
# Allocator Decision
# ==========================================================


def build_investigation_allocator(
    story: list[Any],
    report: InvestigationReport,
) -> None:
    """
    Final allocator conclusion.

    This section represents the executive verdict
    of the Institutional Investigation System.
    """

    story.extend(

        build_section_title(

            "Institutional Allocator Verdict",

        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "After evaluating every completed analytical "
                    "domain, the Institutional Investigation System "
                    "performed allocator synthesis using the canonical "
                    "Investigation Context."
                ),

                (
                    "The decision below represents the final "
                    "institutional assessment of the investigation."
                ),

            ]

        )

    )

    allocator = report.allocator

    if allocator is None:

        story.extend(

            build_narrative(

                [

                    (
                        "Allocator results are currently unavailable "
                        "for this investigation."

                    )

                ]

            )

        )

        return

    story.append(

        KeepTogether(

            [

                build_key_value_table(

                    {

                        "Final Decision":
                            _value(allocator.decision),

                        "Confidence":
                            f"{allocator.confidence:.2f}%",

                        "Residual Risk":
                            _value(allocator.residual_risk),

                        "Required Actions":
                            str(
                                len(
                                    allocator.required_actions,
                                )
                            ),

                    }

                ),

                *build_narrative(

                    [

                        "Allocator Assessment",

                        allocator.rationale,

                    ]

                ),

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

            build_narrative(

                [

                    "Required Actions",

                    *[
                        f"• {action}"
                        for action in actions
                    ],

                ]

            )

        )

    story.extend(

        build_narrative(

            [

                (
                    "The allocator verdict is fully reproducible from "
                    "the canonical Investigation Context. Every "
                    "conclusion presented within this report can be "
                    "independently reconstructed using the same "
                    "validated evidence and analytical workflow."
                )

            ]

        )

    )