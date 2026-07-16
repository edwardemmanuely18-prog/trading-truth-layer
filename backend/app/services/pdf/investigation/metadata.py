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
# Investigation Metadata
# ==========================================================


def build_investigation_metadata(
    story: list[Any],
    report: InvestigationReport,
) -> None:
    """
    Canonical investigation provenance.

    Documents the origin of the investigation,
    participating institutional engines and the
    canonical investigation context used to
    generate this report.
    """

    metadata = report.metadata or {}

    allocator_metadata = (
        report.allocator.metadata
        if report.allocator
        else {}
    ) or {}

    provider_names = metadata.get(
        "provider_names",
        [],
    )

    provider_text = (
        ", ".join(provider_names)
        if provider_names
        else "Unavailable"
    )

    story.extend(

        build_section_title(
            "Investigation Metadata",
        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "This section documents the institutional "
                    "provenance of the investigation and identifies "
                    "the canonical investigation context from which "
                    "every conclusion in this report was derived."
                ),

                (
                    "The metadata below provides transparency over "
                    "the investigation scope, participating engines, "
                    "provider coverage and generation context."
                ),

            ]

        )

    )

    story.append(

        build_key_value_table(

            {

                "Investigation Engine":
                    "Institutional Investigation System (IIS)",

                "Generated":
                    str(report.generated_at),

                "Workspace ID":
                    str(report.workspace_id),

                "Scope":
                    report.scope.value,

                "Status":
                    report.status.value,

                "Completed Domains":
                    str(
                        allocator_metadata.get(
                            "completed_domains",
                            0,
                        )
                    ),

                "Provider Count":
                    str(
                        metadata.get(
                            "provider_count",
                            0,
                        )
                    ),

                "Providers":
                    provider_text,

            }

        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "Every investigation artefact contained within "
                    "this report is generated from the canonical "
                    "Investigation Context and is reproducible from "
                    "the underlying evidence graph."
                )

            ]

        )

    )