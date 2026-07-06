from collections import defaultdict

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.claim_schema import ClaimSchema
from app.models.review_statement import ReviewStatement
from app.models.claim_dispute import ClaimDispute
from app.models.audit_event import AuditEvent
from app.models.integrity_alert import IntegrityAlert
from app.models.integrity_scan import IntegrityScan
from app.models.import_batch import ImportBatch
from app.models.account_snapshot import AccountSnapshot
from app.models.broker_account import BrokerAccount
from app.models.trade import Trade
from app.models.broker_connection import BrokerConnection

import json
from sqlalchemy import or_


MAX_GRAPH_NODES = 3000
MAX_GRAPH_EDGES = 12000


NODE_COLORS = {

    "CLAIM": "#2563eb",

    "TRADE": "#16a34a",

    "BROKER_ACCOUNT": "#16a34a",

    "BROKER_CONNECTION": "#15803d",

    "IMPORT_BATCH": "#06b6d4",

    "CSV_IMPORT": "#f59e0b",

    "AUDIT_EVENT": "#9333ea",

    "INTEGRITY_ALERT": "#dc2626",

    "INTEGRITY_SCAN": "#ef4444",

    "CLAIM_HASH": "#64748b",

    "ACCOUNT_SNAPSHOT": "#0891b2",

    "REVIEW": "#3b82f6",

    "DISPUTE": "#f97316",

    "RISK": "#dc2626",

    "METADATA": "#6b7280",

    "TRADE_SOURCE": "#0284C7",

    "VERIFICATION": "#7C3AED",

    "TRUST_TIER": "#F59E0B",

    "FINGERPRINT": "#14B8A6",

    "HASH": "#64748B",

    "LEDGER": "#1E293B",
}


router = APIRouter(

    prefix="/evidence-graph",

    tags=["Evidence Graph"],
)



class GraphBuilder:

    def __init__(self):

        self.nodes = []

        self.edges = []

        self.node_lookup = {}

        self.relationship_counts = defaultdict(int)

        self.node_degree = defaultdict(int)

        self.layers = defaultdict(list)

        self.layer_titles = {

            0: "Claim",

            1: "Evidence",

            2: "Trades",

            3: "Provenance",

            4: "Integrity",

            5: "Governance",

            6: "Risk",

        }

        self.layer_spacing = 420

        self.node_spacing = 130

        self.claim_lookup = {}

        self.trade_lookup = {}

        self.connection_lookup = {}

        self.account_lookup = {}

        self.import_lookup = {}

        self.snapshot_lookup = {}

        self.review_lookup = {}

        self.dispute_lookup = {}

        self.alert_lookup = {}

        self.scan_lookup = {}

    def add_node(
        self,
        node_id,
        node_type,
        label,
        layer,
        **extra,
    ):

        if node_id in self.node_lookup:
            return

        node = {

            "id": node_id,

            "type": node_type,

            "label": label,

            "layer": layer,

            "color": NODE_COLORS.get(
                node_type,
                "#94a3b8",
            ),
        }

        node.update(extra)

        self.node_lookup[node_id] = node

        self.layers[layer].append(node_id)

        self.nodes.append(node)


    def add_edge(

        self,

        source,

        target,

        relationship,

        weight=1,

    ):

        edge_id = f"{source}_{relationship}_{target}"

        #
        # Prevent duplicate edges.
        #

        if edge_id in self.node_lookup:
            return

        self.node_lookup[edge_id] = True

        self.edges.append({

            "id": edge_id,

            "source": source,

            "target": target,

            "relationship": relationship,

            "weight": weight,

        })

        self.relationship_counts[
            relationship
        ] += 1

        self.node_degree[source] += 1

        self.node_degree[target] += 1


    def build_layout(self):

        layout = {}

        for layer in sorted(self.layers):

            node_ids = self.layers[layer]

            y = 0

            for node_id in node_ids:

                layout[node_id] = {

                    "x":
                        layer
                        * self.layer_spacing,

                    "y":
                        y,

                }

                y += self.node_spacing

        return layout


    def export(self):

        orphan_nodes = []

        for node in self.nodes:

            if node["id"] not in self.node_degree:

                orphan_nodes.append(
                    node["id"]
                )

        node_count = len(self.nodes)

        edge_count = len(self.edges)

        density = 0

        if node_count > 1:

            density = edge_count / (
                node_count * (node_count - 1)
            )

        top_nodes = sorted(

            self.node_degree.items(),

            key=lambda x: x[1],

            reverse=True,

        )[:25]

        layout = self.build_layout()

        return {

            "node_count": node_count,

            "edge_count": edge_count,

            "density": round(
                density,
                6,
            ),

            "nodes":
                self.nodes[:MAX_GRAPH_NODES],

            "edges":
                self.edges[:MAX_GRAPH_EDGES],

            "relationship_counts":
                dict(self.relationship_counts),

            "top_nodes":
                top_nodes,

            "orphan_nodes":
                orphan_nodes[:100],

            "layers": dict(self.layers),

            "layout": layout,

            "layer_titles": self.layer_titles,
        }


    def add_trade(

        self,

        trade,

    ):

        trade_node = f"trade_{trade.id}"

        self.trade_lookup[trade.id] = trade_node

        connection_node = None

        self.add_node(

            trade_node,

            "TRADE",

            trade.symbol,

            layer=2,

            trade_id=trade.id,

            symbol=trade.symbol,

            side=trade.side,

            quantity=trade.quantity,

            pnl=trade.net_pnl,

            verification_state=trade.verification_state,

            trust_tier=trade.evidence_trust_tier,

        )

        #
        # Provenance
        #

        if trade.broker_connection_id:

            source = "LIVE BROKER"

        elif trade.import_source:

            source = "CSV IMPORT"

        else:

            source = "MANUAL"

        source_node = (

            f"trade_source_{trade.id}"

        )

        self.add_node(

            source_node,

            "TRADE_SOURCE",

            source,

            layer=3,

        )

        self.add_edge(

            trade_node,

            source_node,

            "GENERATED_FROM",

        )

        #
        # Verification
        #

        verification_node = (

            f"verification_{trade.id}"

        )

        self.add_node(

            verification_node,

            "VERIFICATION",

            trade.verification_state,

            layer=3,

        )

        self.add_edge(

            trade_node,

            verification_node,

            "VERIFIED_BY",

        )

        #
        # Tier
        #

        tier_node = (

            f"tier_{trade.id}"

        )

        self.add_node(

            tier_node,

            "TRUST_TIER",

            trade.evidence_trust_tier,

            layer=3,

        )

        self.add_edge(

            trade_node,

            tier_node,

            "HAS_TIER",

        )

        #
        # Hash
        #

        if trade.raw_trade_hash:

            hash_node = (

                f"hash_{trade.id}"

            )

            self.add_node(

                hash_node,

                "HASH",

                "Trade Hash",

                layer=4,

                hash=trade.raw_trade_hash,

            )

            self.add_edge(

                trade_node,

                hash_node,

                "HAS_HASH",

            )

        #
        # Fingerprint
        #

        if trade.trade_fingerprint:

            fingerprint = (

                f"fingerprint_{trade.id}"

            )

            self.add_node(

                fingerprint,

                "FINGERPRINT",

                "Fingerprint",

                layer=4,

                fingerprint=trade.trade_fingerprint,

            )

            self.add_edge(

                trade_node,

                fingerprint,

                "HAS_FINGERPRINT",

            )

        #
        # Broker Connection
        #

        if trade.broker_connection_id:

            connection_node = (
                f"connection_{trade.broker_connection_id}"
            )

            self.add_node(
                connection_node,
                "BROKER_CONNECTION",
                f"Connection #{trade.broker_connection_id}",
                layer=4,
                connection_id=trade.broker_connection_id,
                provider=getattr(
                    trade,
                    "import_source",
                    None,
                ),
            )

            self.add_edge(
                trade_node,
                connection_node,
                "SYNCED_FROM",
            )

        #
        # Broker Account
        #

        if trade.broker_account_id:

            account_node = (
                f"account_{trade.broker_account_id}"
            )

            self.add_node(
                account_node,
                "BROKER_ACCOUNT",
                trade.broker_account_id,
                layer=5,
            )

            if connection_node:

                self.add_edge(
                    connection_node,
                    account_node,
                    "USES_ACCOUNT",
                )

        #
        # Import Batch
        #

        if trade.import_job_id:

            import_node = (
                f"import_{trade.import_job_id}"
            )

            self.add_node(
                import_node,
                "IMPORT_BATCH",
                f"Batch {trade.import_job_id}",
                layer=4,
            )

            self.add_edge(
                trade_node,
                import_node,
                "IMPORTED_FROM",
            )


    def add_claim(

        self,

        claim,

    ):

        claim_node = f"claim_{claim.id}"

        self.add_node(

            claim_node,

            "CLAIM",

            claim.name,

            layer=0,

            claim_id=claim.id,

            status=getattr(
                claim,
                "status",
                None,
            ),

            workspace_id=getattr(
                claim,
                "workspace_id",
                None,
            ),
        )

        self.claim_lookup[
            claim.id
        ] = claim_node

        #
        # Claim Hash
        #

        claim_hash = getattr(
            claim,
            "claim_hash",
            None,
        )

        if claim_hash:

            hash_node = (

                f"claim_hash_{claim.id}"

            )

            self.add_node(

                hash_node,

                "HASH",

                "Claim Hash",

                layer=1,

                hash=claim_hash,

            )

            self.add_edge(

                claim_node,

                hash_node,

                "HAS_HASH",

            )

        #
        # Trade Ledger
        #

        ledger_node = (

            f"ledger_{claim.id}"

        )

        self.add_node(

            ledger_node,

            "LEDGER",

            "Trade Ledger",

            layer=1,

        )

        self.add_edge(

            claim_node,

            ledger_node,

            "GENERATED_FROM",

        )


    def resolve_claim_trade_set(

        self,

        claim,

        trades,

    ):

        """
        Resolve the exact evidence set that belongs
        to this claim.

        Every other investigation layer should use
        this method instead of workspace trades.
        """

        locked = getattr(

            claim,

            "locked_trade_ids_json",

            None,

        )

        #
        # Locked evidence
        #

        if locked:

            try:

                ids = set(
                    json.loads(
                        locked
                    )
                )

                return [

                    trade

                    for trade in trades

                    if trade.id in ids

                ]

            except Exception:

                pass

        #
        # Fallback
        #

        return [

            trade

            for trade in trades

            if trade.workspace_id
            == claim.workspace_id

        ]


    def connect_claim_trades(

        self,

        claim,

        trades,

    ):

        claim_node = self.claim_lookup.get(
            claim.id
        )

        if not claim_node:
            return

        ledger_node = f"ledger_{claim.id}"

        #
        # Determine the claim's trade set.
        #

        claim_trades = self.resolve_claim_trade_set(

            claim,

            trades,

        )

        locked = getattr(
            claim,
            "locked_trade_ids_json",
            None,
        )

        if locked:

            try:

                trade_ids = json.loads(
                    locked
                )

            except Exception:

                trade_ids = []

        #
        # If no explicit trade list exists,
        # fall back to all workspace trades.
        #

        if not trade_ids:

            for trade in trades:

                if (
                    trade.workspace_id
                    == claim.workspace_id
                ):

                    trade_ids.append(
                        trade.id
                    )

        #
        # Build relationships.
        #

        for trade in claim_trades:

            trade_node = (
                self.trade_lookup.get(
                    trade.id
                )
            )

            if not trade_node:
                continue

            self.add_edge(

                ledger_node,

                trade_node,

                "CONTAINS",

            )

            self.add_edge(

                claim_node,

                trade_node,

                "SUPPORTED_BY",

            )

    def connect_trade_infrastructure(

        self,

        trade,

        broker_connections,

        broker_accounts,

        account_snapshots,

        import_batches,

    ):

        trade_node = self.trade_lookup.get(
            trade.id
        )

        if not trade_node:
            return

        #
        # ---------------------------------------------------------
        # Broker Connection
        # ---------------------------------------------------------
        #

        connection = next(

            (
                c
                for c in broker_connections
                if c.id == trade.broker_connection_id
            ),

            None,

        )

        connection_node = None

        if connection:

            connection_node = (
                f"connection_{connection.id}"
            )

            self.add_node(

                connection_node,

                "BROKER_CONNECTION",

                connection.connection_name,

                layer=4,

                provider=connection.provider,

                trust_tier=connection.trust_tier,

                verification=connection.verification_status,

                status=connection.connection_status,

                environment=connection.account_environment,

            )

            self.add_edge(

                trade_node,

                connection_node,

                "SYNCED_FROM",

            )

        #
        # ---------------------------------------------------------
        # Broker Account
        # ---------------------------------------------------------
        #

        account = next(

            (
                a
                for a in broker_accounts
                if (
                    a.broker_account_id
                    == trade.broker_account_id
                )
            ),

            None,

        )

        account_node = None

        if account:

            account_node = (
                f"account_{account.id}"
            )

            self.add_node(

                account_node,

                "BROKER_ACCOUNT",

                account.account_name
                or account.broker_account_id,

                layer=5,

                currency=account.currency,

                environment=account.environment,

                status=account.status,

            )

            if connection_node:

                self.add_edge(

                    connection_node,

                    account_node,

                    "USES_ACCOUNT",

                )

        #
        # ---------------------------------------------------------
        # Latest Account Snapshot
        # ---------------------------------------------------------
        #

        if account:

            snapshots = [

                s

                for s in account_snapshots

                if (
                    s.broker_account_id
                    == trade.broker_connection_id
                )

            ]

            if snapshots:

                snapshot = sorted(

                    snapshots,

                    key=lambda s:
                        s.snapshot_time,

                    reverse=True,

                )[0]

                snapshot_node = (

                    f"snapshot_{snapshot.id}"

                )

                self.add_node(

                    snapshot_node,

                    "ACCOUNT_SNAPSHOT",

                    "Account Snapshot",

                    layer=6,

                    balance=snapshot.balance,

                    equity=snapshot.equity,

                    margin=snapshot.margin,

                    free_margin=snapshot.free_margin,

                    leverage=snapshot.leverage,

                )

                if account_node:

                    self.add_edge(

                        account_node,

                        snapshot_node,

                        "HAS_SNAPSHOT",

                    )

        #
        # ---------------------------------------------------------
        # Import Batch
        # ---------------------------------------------------------
        #

        if trade.import_job_id:

            batch = next(

                (
                    b
                    for b in import_batches
                    if b.ingestion_session_id
                    == trade.import_job_id
                ),

                None,

            )

            if batch:

                batch_node = (
                    f"batch_{batch.id}"
                )

                self.add_node(

                    batch_node,

                    "IMPORT_BATCH",

                    batch.filename,

                    layer=4,

                    adapter=batch.adapter_name,

                    source=batch.source_type,

                    imported=batch.rows_imported,

                    rejected=batch.rows_rejected,

                )

                self.add_edge(

                    trade_node,

                    batch_node,

                    "IMPORTED_FROM",

                )


    def connect_claim_governance(

        self,

        claim,

        reviews,

        disputes,

        audit_events,

        alerts,

        scans,

    ):

        claim_node = self.claim_lookup.get(
            claim.id
        )

        if not claim_node:
            return

        #
        # -------------------------------------------------------
        # Reviews
        # -------------------------------------------------------
        #

        for review in reviews:

            if getattr(
                review,
                "claim_schema_id",
                None,
            ) != claim.id:

                continue

            review_node = (
                f"review_{review.id}"
            )

            self.add_node(

                review_node,

                "REVIEW",

                getattr(
                    review,
                    "review_type",
                    "Review",
                ),

                layer=2,

                status=getattr(
                    review,
                    "status",
                    None,
                ),

            )

            self.add_edge(

                claim_node,

                review_node,

                "REVIEWED_BY",

            )

        #
        # -------------------------------------------------------
        # Disputes
        # -------------------------------------------------------
        #

        for dispute in disputes:

            if getattr(
                dispute,
                "claim_schema_id",
                None,
            ) != claim.id:

                continue

            dispute_node = (
                f"dispute_{dispute.id}"
            )

            self.add_node(

                dispute_node,

                "DISPUTE",

                getattr(
                    dispute,
                    "status",
                    "Dispute",
                ),

                layer=2,

            )

            self.add_edge(

                claim_node,

                dispute_node,

                "DISPUTED_BY",

            )

        #
        # -------------------------------------------------------
        # Audit Events
        # -------------------------------------------------------
        #

        for audit in audit_events:

            if str(
                audit.workspace_id
            ) != str(
                claim.workspace_id
            ):

                continue

            audit_node = (
                f"audit_{audit.id}"
            )

            self.add_node(

                audit_node,

                "AUDIT_EVENT",

                audit.event_type,

                layer=3,

                entity=audit.entity_type,

            )

            self.add_edge(

                claim_node,

                audit_node,

                "AUDITED_BY",

            )

        #
        # -------------------------------------------------------
        # Integrity Alerts
        # -------------------------------------------------------
        #

        for alert in alerts:

            if (
                alert.workspace_id
                != claim.workspace_id
            ):

                continue

            alert_node = (
                f"alert_{alert.id}"
            )

            self.add_node(

                alert_node,

                "INTEGRITY_ALERT",

                alert.alert_type,

                layer=4,

                severity=alert.severity,

                status=alert.status,

            )

            self.add_edge(

                claim_node,

                alert_node,

                "HAS_EXCEPTION",

            )

        #
        # -------------------------------------------------------
        # Integrity Scans
        # -------------------------------------------------------
        #

        for scan in scans:

            if (
                scan.workspace_id
                != claim.workspace_id
            ):

                continue

            scan_node = (
                f"scan_{scan.id}"
            )

            self.add_node(

                scan_node,

                "INTEGRITY_SCAN",

                scan.status,

                layer=4,

                claims=scan.claims_scanned,

                alerts=scan.alerts_found,

            )

            self.add_edge(

                claim_node,

                scan_node,

                "SCANNED_BY",

            )


    def build_investigation_summary(

        self,

        claim,

        trades,

        alerts,

        audits,

    ):

        workspace_trades = self.resolve_claim_trade_set(

            claim,

            trades,

        )

        tier1 = len([

            t

            for t in workspace_trades

            if t.evidence_trust_tier == "tier_1"

        ])

        tier2 = len([

            t

            for t in workspace_trades

            if t.evidence_trust_tier == "tier_2"

        ])

        tier3 = len([

            t

            for t in workspace_trades

            if t.evidence_trust_tier == "tier_3"

        ])

        broker_trades = len([

            t

            for t in workspace_trades

            if t.broker_connection_id

        ])

        csv_trades = len([

            t

            for t in workspace_trades

            if t.import_job_id

        ])

        manual_trades = len([

            t

            for t in workspace_trades

            if (
                not t.broker_connection_id
                and not t.import_job_id
            )

        ])

        duplicate_hashes = len(

            workspace_trades

        ) - len({

            t.raw_trade_hash

            for t in workspace_trades

            if t.raw_trade_hash

        })

        missing_hash = len([

            t

            for t in workspace_trades

            if not t.raw_trade_hash

        ])

        missing_fingerprint = len([

            t

            for t in workspace_trades

            if not t.trade_fingerprint

        ])

        integrity_alerts = len([

            a

            for a in alerts

            if a.workspace_id == claim.workspace_id

        ])

        audit_events = len([

            a

            for a in audits

            if str(a.workspace_id)
            == str(claim.workspace_id)

        ])

        trust_score = 100

        trust_score -= tier3 * 8

        trust_score -= duplicate_hashes * 10

        trust_score -= missing_hash * 4

        trust_score -= missing_fingerprint * 3

        trust_score -= integrity_alerts * 5

        trust_score = max(
            0,
            min(
                100,
                trust_score,
            ),
        )

        if trust_score >= 90:

            risk = "LOW"

            recommendation = "VERIFIED"

        elif trust_score >= 70:

            risk = "MEDIUM"

            recommendation = "REVIEW"

        else:

            risk = "HIGH"

            recommendation = "INVESTIGATE"

        return {

            "trust_score": trust_score,

            "risk_level": risk,

            "recommendation": recommendation,

            "broker_trades": broker_trades,

            "csv_trades": csv_trades,

            "manual_trades": manual_trades,

            "tier1": tier1,

            "tier2": tier2,

            "tier3": tier3,

            "duplicate_hashes": duplicate_hashes,

            "missing_hash": missing_hash,

            "missing_fingerprint": missing_fingerprint,

            "integrity_alerts": integrity_alerts,

            "audit_events": audit_events,

            "trade_count": len(workspace_trades),

        }


    def build_risk_layer(

        self,

        claim,

        trades,

    ):

        risk_node = f"risk_{claim.id}"

        self.add_node(

            risk_node,

            "RISK",

            "Investigation Risk",

            layer=6,

        )

        claim_node = self.claim_lookup.get(
            claim.id
        )

        if claim_node:

            self.add_edge(

                claim_node,

                risk_node,

                "HAS_RISK",

            )

        workspace_trades = self.resolve_claim_trade_set(

            claim,

            trades,

        )

        for trade in workspace_trades:

            if trade.evidence_trust_tier == "tier_3":

                node = f"tier3_{trade.id}"

                self.add_node(

                    node,

                    "RISK",

                    "Tier 3 Trade",

                    layer=6,

                )

                self.add_edge(

                    risk_node,

                    node,

                    "HAS_EXCEPTION",

                )

            if not trade.raw_trade_hash:

                node = f"missing_hash_{trade.id}"

                self.add_node(

                    node,

                    "RISK",

                    "Missing Hash",

                    layer=6,

                )

                self.add_edge(

                    risk_node,

                    node,

                    "HAS_EXCEPTION",

                )

            if not trade.trade_fingerprint:

                node = f"missing_fp_{trade.id}"

                self.add_node(

                    node,

                    "RISK",

                    "Missing Fingerprint",

                    layer=6,

                )

                self.add_edge(

                    risk_node,

                    node,

                    "HAS_EXCEPTION",

                )

            if (
                not trade.broker_connection_id
                and not trade.import_job_id
            ):

                node = f"manual_{trade.id}"

                self.add_node(

                    node,

                    "RISK",

                    "Manual Trade",

                    layer=6,

                )

                self.add_edge(

                    risk_node,

                    node,

                    "HAS_EXCEPTION",

                )


    def export_mode(
        self,
        mode: str = "full",
    ):

        graph = self.export()

        if mode == "full":
            return graph

        allowed = {
            "critical": {
                "CLAIM",
                "LEDGER",
                "TRADE",
                "VERIFICATION",
                "TRUST_TIER",
                "BROKER_CONNECTION",
                "BROKER_ACCOUNT",
                "HASH",
            },

            "risk": {
                "CLAIM",
                "RISK",
                "INTEGRITY_ALERT",
                "AUDIT_EVENT",
                "BROKER_ACCOUNT",
                "BROKER_CONNECTION",
            },
        }

        if mode not in allowed:
            return graph

        nodes = [

            n

            for n in graph["nodes"]

            if n["type"] in allowed[mode]

        ]

        nodeIds = {

            n["id"]

            for n in nodes

        }

        edges = [

            e

            for e in graph["edges"]

            if (

                e["source"] in nodeIds

                and

                e["target"] in nodeIds

            )

        ]

        graph["nodes"] = nodes

        graph["edges"] = edges

        graph["node_count"] = len(nodes)

        graph["edge_count"] = len(edges)

        return graph


@router.get(
    "/workspace/{workspace_id}",
)
def get_evidence_graph(

    workspace_id: int,

    db: Session = Depends(
        get_db,
    ),

):

    builder = GraphBuilder()

    #
    # -----------------------------------------------------
    # Load datasets
    # -----------------------------------------------------
    #

    claims = (

        db.query(
            ClaimSchema
        )

        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )

        .all()

    )

    trades = (

        db.query(
            Trade
        )

        .filter(
            Trade.workspace_id
            == workspace_id
        )

        .all()

    )

    broker_connections = (

        db.query(
            BrokerConnection
        )

        .filter(
            BrokerConnection.workspace_id
            == workspace_id
        )

        .all()

    )

    broker_accounts = (

        db.query(
            BrokerAccount
        )

        .all()

    )

    account_snapshots = (

        db.query(
            AccountSnapshot
        )

        .filter(
            AccountSnapshot.workspace_id
            == workspace_id
        )

        .all()

    )

    import_batches = (

        db.query(
            ImportBatch
        )

        .filter(
            ImportBatch.workspace_id
            == workspace_id
        )

        .all()

    )

    reviews = (

        db.query(
            ReviewStatement
        )

        .all()

    )

    disputes = (

        db.query(
            ClaimDispute
        )

        .all()

    )

    audits = (

        db.query(
            AuditEvent
        )

        .filter(
            AuditEvent.workspace_id
            == str(workspace_id)
        )

        .all()

    )

    alerts = (

        db.query(
            IntegrityAlert
        )

        .filter(
            IntegrityAlert.workspace_id
            == workspace_id
        )

        .all()

    )

    scans = (

        db.query(
            IntegrityScan
        )

        .filter(
            IntegrityScan.workspace_id
            == workspace_id
        )

        .all()

    )

    #
    # -----------------------------------------------------
    # Claims
    # -----------------------------------------------------
    #

    for claim in claims:

        builder.add_claim(
            claim
        )

    #
    # -----------------------------------------------------
    # Trades
    # -----------------------------------------------------
    #

    for trade in trades:

        builder.add_trade(
            trade
        )

    #
    # -----------------------------------------------------
    # Claim relationships
    # -----------------------------------------------------
    #

    for claim in claims:

        builder.connect_claim_trades(

            claim,

            trades,

        )

    #
    # -----------------------------------------------------
    # Infrastructure
    # -----------------------------------------------------
    #

    for trade in trades:

        builder.connect_trade_infrastructure(

            trade,

            broker_connections,

            broker_accounts,

            account_snapshots,

            import_batches,

        )

    #
    # -----------------------------------------------------
    # Governance
    # -----------------------------------------------------
    #

    for claim in claims:

        builder.connect_claim_governance(

            claim,

            reviews,

            disputes,

            audits,

            alerts,

            scans,

        )

    #
    # -----------------------------------------------------
    # Risk
    # -----------------------------------------------------
    #

    summaries = {}

    for claim in claims:

        summaries[
            claim.id
        ] = builder.build_investigation_summary(

            claim,

            trades,

            alerts,

            audits,

        )

        builder.build_risk_layer(

            claim,

            trades,

        )

    graph = builder.export()

    graph[
        "investigation_summary"
    ] = summaries

    return graph


@router.get(
    "/claim/{claim_id}",
)
def get_claim_graph(

    claim_id: int,

    db: Session = Depends(
        get_db,
    ),

):

    claim = (

        db.query(
            ClaimSchema
        )

        .filter(
            ClaimSchema.id
            == claim_id
        )

        .first()

    )

    if not claim:

        return {

            "error":
                "Claim not found"

        }

    workspace_id = claim.workspace_id

    trades = (

        db.query(
            Trade
        )

        .filter(
            Trade.workspace_id
            == workspace_id
        )

        .all()

    )

    broker_connections = (

        db.query(
            BrokerConnection
        )

        .filter(
            BrokerConnection.workspace_id
            == workspace_id
        )

        .all()

    )

    broker_accounts = (

        db.query(
            BrokerAccount
        )

        .all()

    )

    account_snapshots = (

        db.query(
            AccountSnapshot
        )

        .filter(
            AccountSnapshot.workspace_id
            == workspace_id
        )

        .all()

    )

    import_batches = (

        db.query(
            ImportBatch
        )

        .filter(
            ImportBatch.workspace_id
            == workspace_id
        )

        .all()

    )

    reviews = (

        db.query(
            ReviewStatement
        )

        .all()

    )

    disputes = (

        db.query(
            ClaimDispute
        )

        .all()

    )

    audits = (

        db.query(
            AuditEvent
        )

        .filter(
            AuditEvent.workspace_id
            == str(workspace_id)
        )

        .all()

    )

    alerts = (

        db.query(
            IntegrityAlert
        )

        .filter(
            IntegrityAlert.workspace_id
            == workspace_id
        )

        .all()

    )

    scans = (

        db.query(
            IntegrityScan
        )

        .filter(
            IntegrityScan.workspace_id
            == workspace_id
        )

        .all()

    )

    #
    # Delegate to the existing
    # workspace graph for now.
    #
    # Later this will become a
    # dedicated optimized builder.
    #

    builder = GraphBuilder()

    builder.add_claim(claim)

    claim_trades = builder.resolve_claim_trade_set(
        claim,
        trades,
    )

    for trade in claim_trades:
        builder.add_trade(trade)

    builder.connect_claim_trades(
        claim,
        claim_trades,
    )

    for trade in claim_trades:
        builder.connect_trade_infrastructure(
            trade,
            broker_connections,
            broker_accounts,
            account_snapshots,
            import_batches,
        )

    builder.connect_claim_governance(
        claim,
        reviews,
        disputes,
        audits,
        alerts,
        scans,
    )

    builder.build_risk_layer(
        claim,
        claim_trades,
    )

    mode = "full"

    graph = builder.export_mode(mode)

    graph["investigation_summary"] = {

        claim.id:

            builder.build_investigation_summary(

                claim,

                claim_trades,

                alerts,

                audits,

            )

    }

    return graph


@router.get(
    "/claim/{claim_id}/critical-path",
)
def get_claim_critical_path(
    claim_id:int,
    db:Session=Depends(get_db),
):

    graph = get_claim_graph(
        claim_id,
        db,
    )

    builder = GraphBuilder()

    builder.nodes = graph["nodes"]
    builder.edges = graph["edges"]

    return builder.export_mode(
        "critical"
    )


@router.get(
    "/claim/{claim_id}/risk",
)
def get_claim_risk_graph(
    claim_id:int,
    db:Session=Depends(get_db),
):

    graph = get_claim_graph(
        claim_id,
        db,
    )

    builder = GraphBuilder()

    builder.nodes = graph["nodes"]
    builder.edges = graph["edges"]

    return builder.export_mode(
        "risk"
    )


@router.get(
    "/claim/{claim_id}/full",
)
def get_claim_full_graph(
    claim_id:int,
    db:Session=Depends(get_db),
):

    return get_claim_graph(
        claim_id,
        db,
    )