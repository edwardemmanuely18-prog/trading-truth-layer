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


def _clean(value) -> str:

    if value is None:
        return "Not Available"

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
# Investigation Graph
# ==========================================================


def build_investigation_graph(
    story: list[Any],
    report: InvestigationReport,
) -> None:
    """
    Executive Investigation Graph Summary.

    Provides a concise overview of the structural
    characteristics of the Investigation Graph.
    """

    story.extend(

        build_section_title(

            "Investigation Graph Summary",

        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "The Investigation Graph represents the structural "
                    "foundation of the Institutional Investigation "
                    "System. It connects evidence, findings, entities "
                    "and analytical reasoning into a single traceable "
                    "investigation model."
                ),

                (
                    "Rather than evaluating isolated evidence, the "
                    "allocator considers the complete relationship "
                    "network reconstructed during the investigation."
                ),

            ]

        )

    )

    graph = report.graph

    statistics = {}

    if graph:

        statistics = getattr(
            graph,
            "statistics",
            {},
        ) or {}

    node_count = len(report.nodes)

    relationship_count = len(report.relationships)

    table = {

        "Evidence Nodes":
            f"{node_count:,}",

        "Relationships":
            f"{relationship_count:,}",

    }

    density = statistics.get("density")

    if density is not None:

        table["Graph Density"] = f"{float(density):.3f}"

    connected = statistics.get(
        "connected_components"
    )

    if connected not in (
        None,
        "",
        "Unknown",
    ):

        table["Connected Components"] = connected

    degree = statistics.get(
        "average_degree"
    )

    if degree not in (
        None,
        "",
        "Unknown",
    ):

        table["Average Degree"] = degree

    story.append(

        build_key_value_table(
            table,
        )

    )

    summary = []

    if node_count:

        summary.append(

            f"The investigation graph contains {node_count:,} evidence node(s)."

        )

    if relationship_count:

        summary.append(

            f"{relationship_count:,} validated relationship(s) were reconstructed across the investigation."

        )

    summary.append(

        (
            "These structural relationships strengthen investigation "
            "traceability by linking evidence, analytical domains and "
            "allocator reasoning into a reproducible investigation model."
        )

    )

    story.extend(

        build_narrative(

            summary,

        )

    )