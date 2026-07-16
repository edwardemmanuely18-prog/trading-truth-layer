from __future__ import annotations

from dataclasses import dataclass

from .context_builder import InvestigationContext

from .models import (
    InvestigationNode,
    InvestigationRelationship,
)


@dataclass(slots=True)
class InvestigationGraph:

    nodes: list[InvestigationNode]

    relationships: list[InvestigationRelationship]

    statistics: dict


# ============================================================
# Graph Builder
# ============================================================

class InvestigationGraphBuilder:

    @staticmethod
    def build(
        context: InvestigationContext,
    ) -> InvestigationGraph:

        payloads = context.provider_payloads

        execution = payloads.get("execution")

        tvs = payloads.get("tvs")

        broker = payloads.get("broker")

        reviews = payloads.get("reviews")

        audit = payloads.get("audit")

        sync_jobs = payloads.get("sync_jobs")

        evidence = payloads.get("evidence_graph")

        nodes: list[InvestigationNode] = []

        relationships: list[InvestigationRelationship] = []

        # ----------------------------------------------------
        # Workspace
        # ----------------------------------------------------

        workspace = context.workspace

        nodes.append(

            InvestigationNode(

                id=f"workspace:{workspace.id}",

                node_type="workspace",

                label=getattr(
                    workspace,
                    "name",
                    f"Workspace {workspace.id}",
                ),

                score=0.0,

            )

        )

        # ----------------------------------------------------
        # Execution Nodes
        # ----------------------------------------------------

        if execution:

            for execution_state in getattr(execution, "executions", []):

                node_id = f"trade:{execution_state.trade_id}"

                nodes.append(

                    InvestigationNode(

                        id=node_id,

                        node_type="trade",

                        label=execution_state.symbol,

                        score=0.0,

                        metadata={

                            "ticket": execution_state.ticket,

                            "status": execution_state.status.name,

                            "account_id": execution_state.account_id,

                            "broker_connection_id": execution_state.broker_connection_id,

                            "opened_at": execution_state.opened_at,

                            "closed_at": execution_state.closed_at,

                        },

                    )

                )

                relationships.append(

                    InvestigationRelationship(

                        source=f"workspace:{workspace.id}",

                        target=node_id,

                        relationship="contains",

                    )

                )

        # ----------------------------------------------------
        # Broker Connections
        # ----------------------------------------------------

        if broker:

            for connection in broker:

                broker_id = f"broker:{connection.id}"

                nodes.append(

                    InvestigationNode(

                        id=broker_id,

                        node_type="broker",

                        score=0.0,

                        label=getattr(
                            connection,
                            "broker_name",
                            "Broker",
                        ),

                    )

                )

                relationships.append(

                    InvestigationRelationship(

                        source=f"workspace:{workspace.id}",

                        target=broker_id,

                        relationship="connected_to",

                    )

                )

        # ----------------------------------------------------
        # Reviews
        # ----------------------------------------------------

        if reviews:

            for review in reviews:

                review_id = f"review:{review.id}"

                nodes.append(

                    InvestigationNode(

                        id=review_id,

                        node_type="review",

                        score=0.0,

                        label=getattr(
                            review,
                            "title",
                            f"Review {review.id}",
                        ),

                    )

                )

        # ----------------------------------------------------
        # Audit
        # ----------------------------------------------------

        if audit:

            for event in audit:

                event_id = f"audit:{event.id}"

                nodes.append(

                    InvestigationNode(

                        id=event_id,

                        node_type="audit",

                        score=0.0,

                        label=getattr(
                            event,
                            "event_type",
                            "Audit",
                        ),

                    )

                )

        # ----------------------------------------------------
        # Sync Jobs
        # ----------------------------------------------------

        if sync_jobs:

            for job in sync_jobs:

                sync_id = f"sync:{job.id}"

                nodes.append(

                    InvestigationNode(

                        id=sync_id,

                        node_type="sync",

                        score=0.0,

                        label=getattr(
                            job,
                            "job_type",
                            "Sync",
                        ),

                    )

                )

        # ----------------------------------------------------
        # TVS
        # ----------------------------------------------------

        if tvs:

            nodes.append(

                InvestigationNode(

                    id="tvs",

                    node_type="verification",

                    score=100.0,

                    label="TVS",

                    metadata=tvs,

                )

            )

        # ----------------------------------------------------
        # Evidence Graph
        # ----------------------------------------------------

        if evidence:

            nodes.append(

                InvestigationNode(

                    id="evidence_graph",

                    node_type="evidence",

                    score=100.0,

                    label="Evidence Graph",

                )

            )

        # ----------------------------------------------------
        # Investigation Relationships
        # ----------------------------------------------------

        trade_nodes = [
            node
            for node in nodes
            if node.node_type == "trade"
        ]

        broker_nodes = [
            node
            for node in nodes
            if node.node_type == "broker"
        ]

        review_nodes = [
            node
            for node in nodes
            if node.node_type == "review"
        ]

        audit_nodes = [
            node
            for node in nodes
            if node.node_type == "audit"
        ]

        sync_nodes = [
            node
            for node in nodes
            if node.node_type == "sync"
        ]

        # Trades -> TVS

        if any(node.id == "tvs" for node in nodes):

            for trade in trade_nodes:

                relationships.append(

                    InvestigationRelationship(

                        source=trade.id,

                        target="tvs",

                        relationship="verified_by",

                    )

                )

        # Trades -> Evidence Graph

        if any(node.id == "evidence_graph" for node in nodes):

            for trade in trade_nodes:

                relationships.append(

                    InvestigationRelationship(

                        source=trade.id,

                        target="evidence_graph",

                        relationship="supported_by",

                    )

                )

        # Broker -> Trade

        broker_lookup = {
            node.id: node
            for node in broker_nodes
        }

        for trade in trade_nodes:

            broker_connection_id = trade.metadata.get(
                "broker_connection_id"
            )

            if broker_connection_id is None:
                continue

            broker_id = (
                f"broker:{broker_connection_id}"
            )

            if broker_id in broker_lookup:

                relationships.append(

                    InvestigationRelationship(

                        source=broker_id,

                        target=trade.id,

                        relationship="executes",

                    )

                )

        # Audit -> Workspace

        for audit in audit_nodes:

            relationships.append(

                InvestigationRelationship(

                    source=audit.id,

                    target=f"workspace:{workspace.id}",

                    relationship="audits",

                )

            )

        # Review -> Workspace

        for review in review_nodes:

            relationships.append(

                InvestigationRelationship(

                    source=review.id,

                    target=f"workspace:{workspace.id}",

                    relationship="reviews",

                )

            )

        # Sync -> Broker

        if broker_nodes:

            for sync in sync_nodes:

                for broker in broker_nodes:

                    relationships.append(

                        InvestigationRelationship(

                            source=sync.id,

                            target=broker.id,

                            relationship="synchronizes",

                        )

                    )

        statistics = {

            "total_nodes": len(nodes),

            "total_relationships": len(relationships),

            "density": (

                len(relationships) / len(nodes)

                if nodes

                else 0

            ),

        }

        return InvestigationGraph(

            nodes=nodes,

            relationships=relationships,

            statistics=statistics,

        )