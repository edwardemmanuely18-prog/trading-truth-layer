from __future__ import annotations

from typing import Any

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


def _count(value) -> str:

    if value is None:
        return "0"

    return f"{len(value):,}"


# ==========================================================
# Investigation Appendix
# ==========================================================


def build_investigation_appendix(
    story: list[Any],
    report: InvestigationReport,
) -> None:
    """
    Executive Technical Appendix.

    Provides a concise audit summary describing
    investigation coverage and reproducibility.
    """

    story.extend(

        build_section_title(

            "Executive Technical Appendix",

        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "This appendix summarizes the institutional "
                    "artifacts consumed during the investigation."
                ),

                (
                    "Its purpose is to provide an executive overview "
                    "of investigation coverage without exposing "
                    "implementation-specific details."
                ),

            ]

        )

    )

    metadata = report.metadata or {}

    providers = metadata.get(
        "provider_names",
        [],
    )

    story.append(

        build_key_value_table(

            {

                "Workspace":
                    metadata.get(
                        "workspace_name",
                        "Not Available",
                    ),

                "Workspace ID":
                    str(report.workspace_id),

                "Investigation Version":
                    metadata.get(
                        "investigation_version",
                        "Not Available",
                    ),

                "Generated":
                    str(report.generated_at),

                "Evidence Nodes":
                    _count(report.nodes),

                "Relationships":
                    _count(report.relationships),

                "Findings":
                    _count(report.findings),

                "Recommendations":
                    _count(report.recommendations),

                "Analytical Domains":
                    "8",

                "Evidence Providers":
                    str(len(providers)),

            }

        )

    )

    if providers:

        provider_text = ", ".join(

            sorted(providers)

        )

        story.extend(

            build_narrative(

                [

                    "Registered Evidence Providers",

                    provider_text,

                ]

            )

        )

    story.extend(

        build_narrative(

            [

                (
                    "The Institutional Investigation Report is fully "
                    "reproducible from the canonical Investigation "
                    "Context maintained by Trading Truth Layer."
                ),

                (
                    "Every analytical conclusion presented in this "
                    "document can be independently reconstructed "
                    "without manual interpretation."
                ),

                (
                    "This concludes the Institutional Investigation "
                    "Report."
                ),

            ]

        )

    )