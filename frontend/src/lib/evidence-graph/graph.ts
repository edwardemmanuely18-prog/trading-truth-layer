import {
    Edge,
    MarkerType,
    Node,
} from "@xyflow/react";

import {
    EvidenceGraphEdge,
    EvidenceGraphNode,
    EvidenceGraphResponse,
    InvestigationEdge,
    InvestigationNode,
} from "./types";

import {
    getNodeColor,
} from "./colors";

/*
|--------------------------------------------------------------------------
| Default layout before hierarchical positioning.
|--------------------------------------------------------------------------
*/

const DEFAULT_COLUMNS = 4;

const COLUMN_WIDTH = 340;

const ROW_HEIGHT = 170;

/*
|--------------------------------------------------------------------------
| Public API
|--------------------------------------------------------------------------
*/

export function buildGraph(
    graph: EvidenceGraphResponse,
): {

    nodes: InvestigationNode[];

    edges: InvestigationEdge[];

} {

    nodeIdMap.clear();

    return {

        nodes: buildNodes(
            graph.nodes,
        ),

        edges: buildEdges(
            graph.edges,
        ),

    };

}

/*
|--------------------------------------------------------------------------
| Node Builder
|--------------------------------------------------------------------------
*/

function buildNodes(
    nodes: EvidenceGraphNode[],
): InvestigationNode[] {

    return nodes.map(

        (
            node,
            index,
        ) => {

            const column =
                index %
                DEFAULT_COLUMNS;

            const row =
                Math.floor(
                    index /
                    DEFAULT_COLUMNS,
                );

            const uniqueId =
                `${node.type}_${node.id}_${index}`;

            nodeIdMap.set(
                node.id,
                uniqueId,
            );

            return {

                id:
                    uniqueId,

                type:
                    "investigation",

                position: {

                    x:
                        column *
                        COLUMN_WIDTH,

                    y:
                        row *
                        ROW_HEIGHT,

                },

                draggable: false,

                selectable: true,

                connectable: false,

                deletable: false,

                data: {

                    id:
                        `${node.type}_${node.id}_${index}`,

                    originalId:
                        node.id,

                    label:
                        node.label,

                    type:
                        node.type,

                    layer:
                        node.layer ?? 0,

                    color:
                        node.color ??
                        getNodeColor(
                            node.type,
                        ),

                    metadata:
                        node.metadata ?? {},

                    search:

                    [
                        node.label,
                        node.type,
                        node.id,
                        ...Object.values(node.metadata ?? {})
                    ]
                    .join(" ")
                    .toLowerCase(),

                },

                style: {

                    width: 260,

                    borderRadius: 12,

                    border:
                        "1px solid #CBD5E1",

                    background:
                        "#FFFFFF",

                    color:
                        "#0F172A",

                    fontSize: 13,

                    fontWeight: 600,

                },

            };

        },

    );

}

/*
|--------------------------------------------------------------------------
| Edge Builder
|--------------------------------------------------------------------------
*/

const nodeIdMap =
    new Map<
        string,
        string
    >();


function buildEdges(
    edges: EvidenceGraphEdge[],
): InvestigationEdge[] {

    return edges.map(

        (
            edge,
            index,
        ) => ({

            id:
                edge.id ??
                `edge_${index}`,

            source:
                nodeIdMap.get(
                    edge.source,
                ) ??
                edge.source,

            target:
                nodeIdMap.get(
                    edge.target,
                ) ??
                edge.target,

            type:
                "smoothstep",

            pathOptions:{
                borderRadius:25,
            },

            animated: false,

            markerEnd: {

                type:
                    MarkerType.ArrowClosed,

            },

            style: {

                strokeWidth: 2,

            },

            label:
                edge.relationship,

            labelStyle: {

                fontSize: 11,

                fontWeight: 600,

            },

            data: {

                relationship:
                    edge.relationship,

                weight:
                    edge.weight,

            },

        }),

    );

}

/*
|--------------------------------------------------------------------------
| Utilities
|--------------------------------------------------------------------------
*/

export function indexNodes(

    nodes: Node[],

): Map<
    string,
    Node
> {

    const map =
        new Map<
            string,
            Node
        >();

    nodes.forEach(

        (
            node,
        ) => {

            map.set(
                node.id,
                node,
            );

        },

    );

    return map;

}

export function outgoingEdges(

    nodeId: string,

    edges: Edge[],

): Edge[] {

    return edges.filter(

        (
            edge,
        ) =>

            edge.source ===
            nodeId,

    );

}

export function incomingEdges(

    nodeId: string,

    edges: Edge[],

): Edge[] {

    return edges.filter(

        (
            edge,
        ) =>

            edge.target ===
            nodeId,

    );

}

export function neighbors(

    nodeId: string,

    edges: Edge[],

): string[] {

    const ids =
        new Set<
            string
        >();

    edges.forEach(

        (
            edge,
        ) => {

            if (
                edge.source ===
                nodeId
            ) {

                ids.add(
                    edge.target,
                );

            }

            if (
                edge.target ===
                nodeId
            ) {

                ids.add(
                    edge.source,
                );

            }

        },

    );

    return [
        ...ids,
    ];

}