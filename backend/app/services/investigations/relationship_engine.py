from __future__ import annotations

from dataclasses import dataclass, field

from .context_builder import InvestigationContext
from .graph_builder import InvestigationGraph


# ============================================================
# Models
# ============================================================

@dataclass(slots=True)
class RelationshipFinding:

    source: str

    target: str

    relationship: str

    confidence: float

    severity: str

    metadata: dict = field(default_factory=dict)


# ============================================================
# Institutional Relationship Engine
# ============================================================

class RelationshipEngine:

    @staticmethod
    def build(
        *,
        context: InvestigationContext,
        graph: InvestigationGraph,
    ) -> list[RelationshipFinding]:

        findings: list[RelationshipFinding] = []

        node_lookup = {
            node.id: node
            for node in graph.nodes
        }

        # ----------------------------------------------------
        # Graph Relationships
        # ----------------------------------------------------

        for edge in graph.relationships:

            findings.append(

                RelationshipFinding(

                    source=edge.source,

                    target=edge.target,

                    relationship=edge.relationship,

                    confidence=1.0,

                    severity="info",

                    metadata=edge.metadata,

                )

            )

        # ----------------------------------------------------
        # Orphan Detection
        # ----------------------------------------------------

        incoming: dict[str, int] = {}

        outgoing: dict[str, int] = {}

        for edge in graph.relationships:

            outgoing[edge.source] = outgoing.get(edge.source, 0) + 1

            incoming[edge.target] = incoming.get(edge.target, 0) + 1

        for node in graph.nodes:

            total = incoming.get(node.id, 0) + outgoing.get(node.id, 0)

            if total == 0:

                findings.append(

                    RelationshipFinding(

                        source=node.id,

                        target="",

                        relationship="orphan",

                        confidence=0.99,

                        severity="warning",

                        metadata={

                            "type": node.node_type,

                        },

                    )

                )

        # ----------------------------------------------------
        # Broker Connectivity
        # ----------------------------------------------------

        for node in graph.nodes:

            if node.node_type != "broker":

                continue

            links = outgoing.get(node.id, 0)

            if links == 0:

                findings.append(

                    RelationshipFinding(

                        source=node.id,

                        target="",

                        relationship="broker_disconnected",

                        confidence=1.0,

                        severity="critical",

                    )

                )

        # ----------------------------------------------------
        # Workspace Coverage
        # ----------------------------------------------------

        workspace_nodes = [

            node

            for node in graph.nodes

            if node.node_type == "workspace"

        ]

        trade_nodes = [

            node

            for node in graph.nodes

            if node.node_type == "trade"

        ]

        if workspace_nodes and not trade_nodes:

            findings.append(

                RelationshipFinding(

                    source=workspace_nodes[0].id,

                    target="",

                    relationship="workspace_without_execution",

                    confidence=1.0,

                    severity="critical",

                )

            )

        # ----------------------------------------------------
        # Duplicate Relationships
        # ----------------------------------------------------

        seen = set()

        duplicates = 0

        for edge in graph.relationships:

            key = (

                edge.source,

                edge.target,

                edge.relationship,

            )

            if key in seen:

                duplicates += 1

            else:

                seen.add(key)

        if duplicates:

            findings.append(

                RelationshipFinding(

                    source="graph",

                    target="graph",

                    relationship="duplicate_relationships",

                    confidence=1.0,

                    severity="medium",

                    metadata={

                        "duplicates": duplicates,

                    },

                )

            )

        # ----------------------------------------------------
        # Relationship Density
        # ----------------------------------------------------

        if graph.statistics["density"] < 0.25:

            findings.append(

                RelationshipFinding(

                    source="graph",

                    target="graph",

                    relationship="low_graph_density",

                    confidence=0.80,

                    severity="medium",

                )

            )

        # ----------------------------------------------------
        # Trade Verification Coverage
        # ----------------------------------------------------

        trade_nodes = [
            node
            for node in graph.nodes
            if node.node_type == "trade"
        ]

        verification_edges = {

            edge.source

            for edge in graph.relationships

            if edge.relationship == "verified_by"

        }

        for trade in trade_nodes:

            if trade.id not in verification_edges:

                findings.append(

                    RelationshipFinding(

                        source=trade.id,

                        target="tvs",

                        relationship="trade_not_verified",

                        confidence=0.95,

                        severity="high",

                        metadata={

                            "symbol": trade.label,

                        },

                    )

                )

        # ----------------------------------------------------
        # Evidence Coverage
        # ----------------------------------------------------

        evidence_edges = {

            edge.source

            for edge in graph.relationships

            if edge.relationship == "supported_by"

        }

        for trade in trade_nodes:

            if trade.id not in evidence_edges:

                findings.append(

                    RelationshipFinding(

                        source=trade.id,

                        target="evidence_graph",

                        relationship="missing_evidence",

                        confidence=0.95,

                        severity="medium",

                        metadata={

                            "symbol": trade.label,

                        },

                    )

                )

        # ----------------------------------------------------
        # Broker Execution Coverage
        # ----------------------------------------------------

        execution_edges = {

            edge.target

            for edge in graph.relationships

            if edge.relationship == "executes"

        }

        for trade in trade_nodes:

            if trade.id not in execution_edges:

                findings.append(

                    RelationshipFinding(

                        source="broker",

                        target=trade.id,

                        relationship="execution_without_broker",

                        confidence=1.0,

                        severity="critical",

                    )

                )

        return findings