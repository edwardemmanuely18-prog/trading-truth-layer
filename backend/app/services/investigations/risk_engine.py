from __future__ import annotations

from dataclasses import dataclass, field

from .context_builder import InvestigationContext
from .graph_builder import InvestigationGraph
from .relationship_engine import RelationshipFinding
from .models import (
    InvestigationTimelineEvent,
)


# ============================================================
# Models
# ============================================================

@dataclass(slots=True)
class RiskFinding:

    id: str

    title: str

    description: str

    severity: str

    confidence: float

    category: str

    recommendation: str

    metadata: dict = field(default_factory=dict)


# ============================================================
# Institutional Risk Engine
# ============================================================

class RiskEngine:

    @staticmethod
    def build(
        *,
        context: InvestigationContext,
        graph: InvestigationGraph,
        relationships: list[RelationshipFinding],
        timeline: list[InvestigationTimelineEvent],
    ) -> list[RiskFinding]:

        findings: list[RiskFinding] = []

        payloads = context.provider_payloads

        execution = payloads.get("execution")

        tvs = payloads.get("tvs")

        broker = payloads.get("broker")

        reviews = payloads.get("reviews", [])

        audit = payloads.get("audit", [])

        sync_jobs = payloads.get("sync_jobs", [])

        # ====================================================
        # Execution Integrity
        # ====================================================

        if execution:

            integrity = execution.integrity

            if integrity.score < 95:

                findings.append(

                    RiskFinding(

                        id="execution_integrity",

                        title="Execution Integrity Reduced",

                        description=(
                            "Execution replay contains integrity anomalies."
                        ),

                        severity="high",

                        confidence=100.0,

                        category="execution",

                        recommendation=(
                            "Inspect duplicate executions, orphan positions "
                            "and replay inconsistencies."
                        ),

                        metadata={

                            "score": integrity.score,

                        },

                    )

                )

        # ====================================================
        # Broker Connectivity
        # ====================================================

        disconnected = [

            r

            for r in relationships

            if r.relationship == "broker_disconnected"

        ]

        if disconnected:

            findings.append(

                RiskFinding(

                    id="broker_connectivity",

                    title="Broker Connectivity Risk",

                    description=(
                        "One or more broker connections are disconnected."
                    ),

                    severity="critical",

                    confidence=100.0,

                    category="broker",

                    recommendation=(
                        "Reconnect affected broker connections."
                    ),

                    metadata={

                        "count": len(disconnected),

                    },

                )

            )

        # ====================================================
        # Orphan Relationships
        # ====================================================

        orphan_nodes = [

            r

            for r in relationships

            if r.relationship == "orphan"

        ]

        if orphan_nodes:

            findings.append(

                RiskFinding(

                    id="orphan_entities",

                    title="Orphan Investigation Entities",

                    description=(
                        "Investigation graph contains isolated entities."
                    ),

                    severity="medium",

                    confidence=95.0,

                    category="graph",

                    recommendation=(
                        "Investigate disconnected entities and missing links."
                    ),

                    metadata={

                        "count": len(orphan_nodes),

                    },

                )

            )

        # ====================================================
        # Sparse Investigation Graph
        # ====================================================

        density = graph.statistics.get(
            "density",
            1,
        )

        if density < 0.25:

            findings.append(

                RiskFinding(

                    id="graph_density",

                    title="Sparse Investigation Graph",

                    description=(
                        "Relationship density is lower than expected."
                    ),

                    severity="medium",

                    confidence=90.0,

                    category="graph",

                    recommendation=(
                        "Increase evidence coverage and relationship mapping."
                    ),

                )

            )

        # ====================================================
        # Review Coverage
        # ====================================================

        if len(reviews) == 0:

            findings.append(

                RiskFinding(

                    id="review_coverage",

                    title="No External Reviews",

                    description=(
                        "No external review statements were found."
                    ),

                    severity="low",

                    confidence=90.0,

                    category="review",

                    recommendation=(
                        "Collect institutional review statements."
                    ),

                )

            )

        # ====================================================
        # Audit Coverage
        # ====================================================

        if len(audit) == 0:

            findings.append(

                RiskFinding(

                    id="audit_coverage",

                    title="Audit Trail Missing",

                    description=(
                        "No audit events were available."
                    ),

                    severity="medium",

                    confidence=95.0,

                    category="audit",

                    recommendation=(
                        "Verify audit logging is enabled."
                    ),

                )

            )

        # ====================================================
        # Synchronization Coverage
        # ====================================================

        if len(sync_jobs) == 0:

            findings.append(

                RiskFinding(

                    id="sync_jobs",

                    title="No Sync History",

                    description=(
                        "No synchronization history was found."
                    ),

                    severity="medium",

                    confidence=100.0,

                    category="sync",

                    recommendation=(
                        "Configure broker synchronization."
                    ),

                )

            )

        # ====================================================
        # TVS Availability
        # ====================================================

        if tvs is None:

            findings.append(

                RiskFinding(

                    id="verification",

                    title="Verification Metrics Missing",

                    description=(
                        "TVS metrics are unavailable."
                    ),

                    severity="critical",

                    confidence=100.0,

                    category="verification",

                    recommendation=(
                        "Recompute TVS metrics."
                    ),

                )

            )

        return findings