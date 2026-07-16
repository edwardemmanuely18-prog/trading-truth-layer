from __future__ import annotations

from dataclasses import dataclass, field

from .graph_builder import InvestigationGraph
from .relationship_engine import RelationshipFinding
from .models import InvestigationFinding
from .models import (
    InvestigationFinding,
    InvestigationTimelineEvent,
)


# ============================================================
# Models
# ============================================================

@dataclass(slots=True)
class CriticalPathStep:

    order: int

    title: str

    category: str

    severity: str

    description: str

    metadata: dict = field(default_factory=dict)


@dataclass(slots=True)
class CriticalPath:

    score: float

    root_cause: str

    steps: list[CriticalPathStep]

    recommendations: list[str]


# ============================================================
# Institutional Critical Path Engine
# ============================================================

class CriticalPathEngine:

    @staticmethod
    def build(

        *,
        graph: InvestigationGraph,

        relationships: list[RelationshipFinding],

        findings: list[InvestigationFinding],

        timeline: list[InvestigationTimelineEvent],

    ) -> CriticalPath:

        steps: list[
            CriticalPathStep
        ] = []

        recommendations: list[
            str
        ] = []

        severity_weight = {

            "CRITICAL": 100,

            "HIGH": 80,

            "MEDIUM": 50,

            "LOW": 20,

            "INFORMATION": 5,

        }

        ranked = sorted(

            findings,

            key=lambda finding: severity_weight.get(

                finding.severity.value
                if hasattr(
                    finding.severity,
                    "value",
                )
                else str(
                    finding.severity,
                ),

                0,

            ),

            reverse=True,

        )

        score = 100.0

        root_cause = (
            "No critical issue detected."
        )

        for index, finding in enumerate(ranked):

            steps.append(

                CriticalPathStep(

                    order=index + 1,

                    title=finding.title,

                    category="General",

                    severity=(
                        finding.severity.value
                        if hasattr(
                            finding.severity,
                            "value",
                        )
                        else str(
                            finding.severity,
                        )
                    ),

                    description=finding.description,

                    metadata={},

                )

            )

            recommendations.append(

                finding.recommendation

            )

        if ranked:

            root_cause = ranked[0].title

        penalties = {

            "CRITICAL": 15,

            "HIGH": 10,

            "MEDIUM": 5,

            "LOW": 2,

        }

        for finding in ranked:

            severity = (

                finding.severity.value

                if hasattr(
                    finding.severity,
                    "value",
                )

                else str(
                    finding.severity,
                )

            )

            score -= penalties.get(

                severity,

                0,

            )

        # Relationship penalties

        duplicate_edges = len(

            [

                r

                for r in relationships

                if r.relationship
                == "duplicate_relationships"

            ]

        )

        score -= duplicate_edges * 2

        orphan_nodes = len(

            [

                r

                for r in relationships

                if r.relationship == "orphan"

            ]

        )

        score -= orphan_nodes

        # Sparse graph penalty

        density = graph.statistics.get(

            "density",

            1.0,

        )

        if density < 0.25:

            score -= 5

        # Missing timeline

        if len(timeline) == 0:

            score -= 10

        score = max(

            0.0,

            min(

                100.0,

                score,

            ),

        )

        return CriticalPath(

            score=round(
                score,
                2,
            ),

            root_cause=root_cause,

            steps=steps,

            recommendations=list(

                dict.fromkeys(

                    recommendations

                )

            ),

        )