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
# Institutional Investigation Pipeline
# ==========================================================


def build_investigation_pipeline(
    story: list[Any],
    report: InvestigationReport,
) -> None:
    """
    Documents the canonical IIS investigation pipeline.

    Explains how canonical investigation evidence flows
    through the Institutional Investigation System before
    producing the allocator decision.
    """

    story.extend(

        build_section_title(
            "Institutional Investigation Pipeline",
        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "The Institutional Investigation System (IIS) "
                    "performs a deterministic multi-domain forensic "
                    "investigation using the canonical Investigation "
                    "Context."
                ),

                (
                    "Each analytical domain executes independently "
                    "before contributing evidence to the allocator "
                    "decision, ensuring that every conclusion remains "
                    "fully traceable and reproducible."
                ),

            ]

        )

    )

    domains = [

        report.execution,

        report.evidence,

        report.verification,

        report.governance,

        report.broker,

        report.synchronization,

        report.review,

        report.behavior,

    ]

    completed_domains = sum(
        domain is not None
        for domain in domains
    )

    allocator = report.allocator

    story.append(

        build_key_value_table(

            {

                "Stage 1":
                    "Canonical Investigation Context",

                "Stage 2":
                    "Execution Analysis",

                "Stage 3":
                    "Evidence Intelligence",

                "Stage 4":
                    "Verification Analysis",

                "Stage 5":
                    "Governance Analysis",

                "Stage 6":
                    "Broker Analysis",

                "Stage 7":
                    "Synchronization Analysis",

                "Stage 8":
                    "Review Analysis",

                "Stage 9":
                    "Behaviour Analysis",

                "Stage 10":
                    "Allocator Decision",

                "Completed Domains":
                    f"{completed_domains}/8",

                "Allocator Decision":
                    _label(
                        allocator.decision
                    )
                    if allocator
                    else "Unavailable",

            }

        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "Unlike conventional rule engines, IIS preserves "
                    "complete lineage across every investigation stage. "
                    "The allocator decision is therefore reproducible "
                    "from the original investigation context through "
                    "every intermediate analytical domain."
                ),

                (
                    "This deterministic pipeline enables independent "
                    "review, institutional governance, regulatory "
                    "inspection and forensic replay without requiring "
                    "re-execution of the investigation."
                ),

            ]

        )

    )