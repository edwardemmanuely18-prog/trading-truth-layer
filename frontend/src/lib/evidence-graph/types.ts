import type {
    Node,
    Edge,
} from "@xyflow/react";

/*
|--------------------------------------------------------------------------
| Backend DTOs
|--------------------------------------------------------------------------
| These interfaces represent the exact objects returned by the
| FastAPI Evidence Graph endpoint.
*/

export interface EvidenceGraphNode {

    id: string;

    claim_id?: number;

    type: string;

    label: string;

    layer: number;

    color?: string;

    status?: string;

    visibility?: string;

    direction?: string;

    observation_type?: string;

    metadata?: Record<string, unknown>;

}

export interface EvidenceGraphEdge {

    id?: string;

    source: string;

    target: string;

    relationship: string;

    weight?: number;

}

/*
|--------------------------------------------------------------------------
| Graph Statistics
|--------------------------------------------------------------------------
*/

export interface GraphStatistics {

    node_count: number;

    edge_count: number;

    density: number;

    relationship_counts: Record<
        string,
        number
    >;

}

export interface InvestigationSummary {

    trust_score: number;

    risk_level: string;

    recommendation: string;

    trade_count: number;

    broker_trades: number;

    csv_trades: number;

    manual_trades: number;

    tier1: number;

    tier2: number;

    tier3: number;

    duplicate_hashes: number;

    missing_hash: number;

    missing_fingerprint: number;

    integrity_alerts: number;

    audit_events: number;

}

/*
|--------------------------------------------------------------------------
| Backend Response
|--------------------------------------------------------------------------
*/

export interface EvidenceGraphResponse {

    node_count: number;

    edge_count: number;

    density: number;

    nodes: EvidenceGraphNode[];

    edges: EvidenceGraphEdge[];

    relationship_counts:
        Record<
            string,
            number
        >;

    top_nodes:
        Array<
            [string, number]
        >;

    orphan_nodes: string[];

    layers:
        Record<
            number,
            string[]
        >;

    statistics?:
        GraphStatistics;

    investigation_summary?:
        Record<
            string,
            InvestigationSummary
        >;

    layout?:
        Record<
            string,
            {
                x: number;
                y: number;
            }
        >;

}

/*
|--------------------------------------------------------------------------
| ReactFlow Model
|--------------------------------------------------------------------------
| These interfaces are used AFTER the graph adapter converts the
| backend DTOs into ReactFlow objects.
*/

export interface InvestigationNode
    extends Node {

    data: {

        id: string;

        label: string;

        type: string;

        layer: number;

        color: string;

        metadata?: Record<
            string,
            unknown
        >;

    };

}

export interface InvestigationEdge
    extends Edge {

    data: {

        relationship: string;

        weight?: number;

    };

}

/*
|--------------------------------------------------------------------------
| Inspector
|--------------------------------------------------------------------------
*/

export interface InspectorState {

    node:
        InvestigationNode | null;

    incoming:
        InvestigationEdge[];

    outgoing:
        InvestigationEdge[];

}