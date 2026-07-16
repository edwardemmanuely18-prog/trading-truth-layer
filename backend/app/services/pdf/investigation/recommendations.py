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


def _execution_type(automated: bool) -> str:

    return (
        "Automatic"
        if automated
        else "Manual Review"
    )


# ==========================================================
# Recommendations
# ==========================================================


def build_investigation_recommendations(
    story: list[Any],
    report: InvestigationReport,
) -> None:
    """
    Institutional remediation roadmap.

    Recommendations are presented as executive
    action cards rather than spreadsheet rows.
    """

    story.extend(

        build_section_title(

            "Institutional Recommendations",

        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "Following completion of the investigation, the "
                    "Institutional Investigation System generated a "
                    "prioritized remediation roadmap."
                ),

                (
                    "Recommendations are ordered according to their "
                    "expected impact on governance, evidence integrity "
                    "and allocator confidence."
                ),

            ]

        )

    )

    recommendations = sorted(

        report.recommendations or [],

        key=lambda recommendation: recommendation.priority,

    )

    if not recommendations:

        story.extend(

            build_narrative(

                [

                    (
                        "No remediation recommendations were produced "
                        "during this investigation."

                    )

                ]

            )

        )

        return

    automatic = 0
    manual = 0

    for recommendation in recommendations:

        if recommendation.automated:
            automatic += 1
        else:
            manual += 1

        story.append(

            KeepTogether(

                [

                    build_key_value_table(

                        {

                            "Priority":
                                str(recommendation.priority),

                            "Recommendation":
                                recommendation.title,

                            "Execution":
                                _execution_type(
                                    recommendation.automated,
                                ),

                        }

                    ),

                    *build_narrative(

                        [

                            recommendation.rationale,

                        ]

                    ),

                ]

            )

        )

    story.extend(

        build_narrative(

            [

                (

                    f"The Institutional Investigation System generated "

                    f"{len(recommendations)} recommendation(s)."

                ),

                (

                    f"{automatic} recommendation(s) may be executed "

                    f"automatically while {manual} require "

                    f"institutional review."

                ),

                (

                    "Recommendations should be implemented in priority "

                    "order to maximize investigation integrity, "

                    "strengthen governance and reduce residual risk."

                ),

            ]

        )

    )