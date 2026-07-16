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
# Critical Path Reconstruction
# ==========================================================


def build_investigation_critical_path(
    story: list[Any],
    report: InvestigationReport,
) -> None:
    """
    Executive presentation of the canonical IIS
    critical reasoning path.

    The objective is to explain why the allocator
    reached its conclusion rather than reproduce
    the internal graph structure.
    """

    story.extend(

        build_section_title(
            "Critical Path Reconstruction",
        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "The critical path represents the principal "
                    "causal reasoning chain reconstructed by the "
                    "Institutional Investigation System (IIS)."
                ),

                (
                    "Unlike the Investigation Graph, the critical "
                    "path highlights only the sequence of analytical "
                    "events that materially influenced the allocator "
                    "decision."
                ),

            ]

        )

    )

    critical_path = report.critical_path

    if critical_path is None:

        story.extend(

            build_narrative(

                [

                    (
                        "No critical reasoning path was identified "
                        "for this investigation."
                    )

                ]

            )

        )

        return

    # ------------------------------------------------------
    # Executive Summary
    # ------------------------------------------------------

    story.append(

        build_key_value_table(

            {

                "Critical Path Score":
                    f"{critical_path.score:.2f}",

                "Root Cause":
                    critical_path.root_cause,

                "Reasoning Steps":
                    str(len(critical_path.steps)),

            }

        )

    )

    # ------------------------------------------------------
    # Sequential Reasoning
    # ------------------------------------------------------

    for step in critical_path.steps:

        story.append(

            KeepTogether(

                [

                    build_key_value_table(

                        {

                            "Step":
                                str(step.order),

                            "Stage":
                                step.title,

                            "Severity":
                                str(step.severity),

                        }

                    ),

                    *build_narrative(

                        [

                            step.description,

                        ]

                    ),

                ]

            )

        )

    # ------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------

    if critical_path.recommendations:

        story.extend(

            build_section_title(
                "Critical Path Actions",
            )

        )

        for index, recommendation in enumerate(

            critical_path.recommendations,

            start=1,

        ):

            story.append(

                KeepTogether(

                    [

                        build_key_value_table(

                            {

                                "Priority":
                                    str(index),

                                "Recommendation":
                                    recommendation,

                            }

                        )

                    ]

                )

            )

    # ------------------------------------------------------
    # Closing Narrative
    # ------------------------------------------------------

    story.extend(

        build_narrative(

            [

                (
                    "The reconstructed critical path demonstrates "
                    "how the allocator progressed from canonical "
                    "evidence through domain analysis to the final "
                    "institutional decision."
                ),

                (
                    "Because every transition remains linked to the "
                    "Investigation Context, the reasoning process can "
                    "be independently reviewed and reproduced without "
                    "loss of forensic traceability."
                ),

            ]

        )

    )