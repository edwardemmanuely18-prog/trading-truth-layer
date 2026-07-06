"""
Trading Truth Layer (TTL)
Institutional Evidence Graph Engine

Graph Investigation Context

This object is the canonical investigation state used by every
builder in the Evidence Graph pipeline.

Pipeline

Relationship Builder
        ↓
Provenance Builder
        ↓
Integrity Builder
        ↓
Governance Builder
        ↓
Risk Builder
        ↓
Summary Builder

Every builder receives the SAME GraphContext instance.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class GraphContext:
    """
    Canonical Investigation Context.

    Stores every entity discovered while investigating
    a claim or workspace.

    This class intentionally contains NO business logic.
    """

    #
    # ------------------------------------------------------------
    # Workspace
    # ------------------------------------------------------------
    #

    workspace_id: int

    #
    # ------------------------------------------------------------
    # Investigation Scope
    # ------------------------------------------------------------
    #

    claim_ids: List[int] = field(
        default_factory=list
    )

    trade_ids: List[int] = field(
        default_factory=list
    )

    broker_connection_ids: List[int] = field(
        default_factory=list
    )

    broker_account_ids: List[int] = field(
        default_factory=list
    )

    import_batch_ids: List[int] = field(
        default_factory=list
    )

    snapshot_ids: List[int] = field(
        default_factory=list
    )

    audit_ids: List[int] = field(
        default_factory=list
    )

    integrity_alert_ids: List[int] = field(
        default_factory=list
    )

    integrity_scan_ids: List[int] = field(
        default_factory=list
    )

    #
    # ------------------------------------------------------------
    # Loaded ORM Objects
    # ------------------------------------------------------------
    #

    claims: List[Any] = field(
        default_factory=list
    )

    trades: List[Any] = field(
        default_factory=list
    )

    broker_connections: List[Any] = field(
        default_factory=list
    )

    broker_accounts: List[Any] = field(
        default_factory=list
    )

    import_batches: List[Any] = field(
        default_factory=list
    )

    account_snapshots: List[Any] = field(
        default_factory=list
    )

    audit_events: List[Any] = field(
        default_factory=list
    )

    integrity_alerts: List[Any] = field(
        default_factory=list
    )

    integrity_scans: List[Any] = field(
        default_factory=list
    )

    #
    # ------------------------------------------------------------
    # Investigation Graph
    # ------------------------------------------------------------
    #

    nodes: List[Dict] = field(
        default_factory=list
    )

    edges: List[Dict] = field(
        default_factory=list
    )

    #
    # ------------------------------------------------------------
    # Fast Lookup Indexes
    # ------------------------------------------------------------
    #

    node_index: Dict[str, Dict] = field(
        default_factory=dict
    )

    edge_index: Dict[str, Dict] = field(
        default_factory=dict
    )

    #
    # ------------------------------------------------------------
    # Integrity
    # ------------------------------------------------------------
    #

    integrity_score: float = 0.0

    integrity_band: str = "UNKNOWN"

    #
    # ------------------------------------------------------------
    # Trust
    # ------------------------------------------------------------
    #

    trust_score: float = 0.0

    trust_band: str = "UNKNOWN"

    #
    # ------------------------------------------------------------
    # Risk
    # ------------------------------------------------------------
    #

    risk_level: str = "UNKNOWN"

    risk_flags: List[Dict] = field(
        default_factory=list
    )

    #
    # ------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------
    #

    metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    #
    # ------------------------------------------------------------
    # Investigation Summary
    # ------------------------------------------------------------
    #

    summary: Dict[str, Any] = field(
        default_factory=dict
    )

    #
    # ------------------------------------------------------------
    # Builder Metadata
    # ------------------------------------------------------------
    #

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    #
    # ------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------
    #

    def add_node(self, node: Dict):

        node_id = node["id"]

        if node_id not in self.node_index:

            self.node_index[node_id] = node

            self.nodes.append(node)

    def add_edge(self, edge: Dict):

        edge_id = edge["id"]

        if edge_id not in self.edge_index:

            self.edge_index[edge_id] = edge

            self.edges.append(edge)

    def update_metric(
        self,
        key: str,
        value: Any,
    ):

        self.metrics[key] = value

    def update_summary(
        self,
        key: str,
        value: Any,
    ):

        self.summary[key] = value

    def add_risk(
        self,
        risk: Dict,
    ):

        self.risk_flags.append(risk)

    def counts(self):

        return {

            "claims":
                len(self.claims),

            "trades":
                len(self.trades),

            "broker_connections":
                len(self.broker_connections),

            "broker_accounts":
                len(self.broker_accounts),

            "imports":
                len(self.import_batches),

            "snapshots":
                len(self.account_snapshots),

            "audits":
                len(self.audit_events),

            "alerts":
                len(self.integrity_alerts),

            "scans":
                len(self.integrity_scans),

            "nodes":
                len(self.nodes),

            "edges":
                len(self.edges),
        }