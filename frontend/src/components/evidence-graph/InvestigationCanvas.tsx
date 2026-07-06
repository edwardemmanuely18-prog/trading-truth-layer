"use client";

import {
    useMemo,
    useEffect,
    useRef,
    useState,
} from "react";


import {
    Background,
    Controls,
    MiniMap,
    ReactFlow,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import {
    buildGraph,
} from "@/lib/evidence-graph/graph";

import {

    applyInvestigationLayout,

    LAYER_SPACING,

    LAYER_TITLES,

    NODE_WIDTH,

} from "@/lib/evidence-graph/layout";

import {

    CANVAS,

    GRID,

    NODE,

    VIEWPORT,

} from "@/lib/evidence-graph/canvasGeometry";

import {
    EvidenceGraphResponse,
} from "@/lib/evidence-graph/types";

import InvestigationNode from "./InvestigationNode";

import GraphEdge from "./GraphEdge";

interface Props {

    graph: EvidenceGraphResponse;

    selectedClaimId?: string;

    selectedNodeId?: string;

    onNodeSelect?: (
        nodeId: string,
    ) => void;

    onCriticalPath?: () => void;

    onRiskOnly?: () => void;

    onExpand?: () => void;

    onCollapse?: () => void;

}

export default function InvestigationCanvas({

    graph,

    selectedClaimId,

    selectedNodeId,

    onNodeSelect,

    onCriticalPath,

    onRiskOnly,

    onExpand,

    onCollapse,

}: Props) {

    const flowRef = useRef<any>(null);

    const [showLegend, setShowLegend] =
        useState(true);

    const [showLayerHeaders, setShowLayerHeaders] =
        useState(true);

    const [showHashes, setShowHashes] =
        useState(true);

    const {

        nodes,

        edges,

    } = useMemo(() => {

        const built =
            buildGraph(graph);

        return applyInvestigationLayout(

            built.nodes,

            built.edges,

        );

    }, [graph]);

    const preparedNodes = nodes
        .filter((node) => {

            if (showHashes) {
                return true;
            }

            return (
                !String(
                    node.data?.type ?? ""
                )
                    .toLowerCase()
                    .includes("hash")
            );

        })
        .map((node) => ({

            ...node,

            type: "investigation",

            selected:
                node.id === selectedNodeId,

            data: {

                ...node.data,

                selectedClaimId,

                onSelect: () =>
                    onNodeSelect?.(
                        node.id,
                    ),

            },

        }));

    useEffect(() => {

        if (!selectedClaimId) {

            flowRef.current?.fitView({

                padding: 0.20,

            });

            return;

        }

        const claimNodes = preparedNodes.filter(

            node =>

                node.id.includes(selectedClaimId)

        );

        if (claimNodes.length) {

            flowRef.current?.fitView({

                nodes: claimNodes,

                padding: 0.30,

                duration: 700,

            });

            setTimeout(() => {

                flowRef.current?.fitView({

                    padding: 0.20,

                    duration: 700,

                });

            }, 100);

        }

    }, [

        selectedClaimId,

        preparedNodes,


    ]);

    return (

        <div
            className="
            relative
            h-[900px]
            w-full
            overflow-hidden
            rounded-xl
            border
            bg-white
            "
        >
        

            {showLayerHeaders && (

            <div
                className="absolute left-0 top-0 z-10 pointer-events-none"
                style={{
                    width: "100%",
                    height: 80,
                }}
            >

                {LAYER_TITLES.map((title, index) => (

                    <div
                        key={title}
                        className="
                        absolute
                        top-12
                        transition-all
                        duration-300
                        "
                        style={{
                            left:
                                CANVAS.WIDTH_PADDING +
                                index * GRID.COLUMN_SPACING,

                            width: NODE.WIDTH,

                            textAlign: "center",
                        }}
                    >

                        <div
                            className="
                            rounded-lg
                            bg-slate-900
                            text-white
                            text-xs
                            font-semibold
                            py-2
                            truncate
                            shadow
                            "
                        >
                            {title}
                        </div>

                    </div>

                ))}

            </div>

            )}

            <div
            className="
            flex
            flex-wrap
            items-center
            gap-2
            border-b
            bg-slate-50
            px-4
            py-3
            "
            >

            <button

            onClick={()=>

            flowRef.current?.fitView({

            padding:0.25,

            duration:700,

            })

            }

            className="rounded border px-3 py-1 hover:bg-slate-100"

            >

            Fit Claim

            </button>

            <button

            onClick={onCriticalPath}

            className="rounded border px-3 py-1 hover:bg-slate-100"

            >

            Critical Path

            </button>

            <button

            onClick={onRiskOnly}

            className="rounded border px-3 py-1 hover:bg-slate-100"

            >

            Risk Only

            </button>

            <button

            onClick={()=>

            setShowHashes(

            v=>!v

            )

            }

            className="rounded border px-3 py-1 hover:bg-slate-100"

            >

            {showHashes

            ?

            "Hide Hashes"

            :

            "Show Hashes"}

            </button>

            <button

            onClick={onExpand}

            className="rounded border px-3 py-1 hover:bg-slate-100"

            >

            Expand

            </button>

            <button

            onClick={onCollapse}

            className="rounded border px-3 py-1 hover:bg-slate-100"

            >

            Collapse

            </button>

            <button

            onClick={()=>

            setShowLayerHeaders(

            v=>!v

            )

            }

            className="rounded border px-3 py-1 hover:bg-slate-100"

            >

            Layers

            </button>

            <button

            onClick={()=>

            setShowLegend(

            v=>!v

            )

            }

            className="rounded border px-3 py-1 hover:bg-slate-100"

            >

            Legend

            </button>

            </div>

            <div
            className="
            absolute
            left-0
            right-0
            bottom-0
            top-14
            "
            >

            <ReactFlow

                onInit={(instance) => {

                    flowRef.current = instance;

                }}

                nodes={preparedNodes}

                edges={edges}

                fitView

                fitViewOptions={{

                    padding: VIEWPORT.FIT_PADDING,

                    duration:700,

                }}

                nodeTypes={{
                    investigation: InvestigationNode,
                }}

                edgeTypes={{

                    investigation: GraphEdge,

                }}

                nodesDraggable={false}

                nodesConnectable={false}

                elementsSelectable

                panOnDrag

                zoomOnScroll

                minZoom={VIEWPORT.MIN_ZOOM}

                maxZoom={VIEWPORT.MAX_ZOOM}

                selectionOnDrag={false}

                zoomOnDoubleClick={false}

            >

                <Background
                    gap={28}
                    size={1.5}
                />

                <MiniMap
                    pannable
                    zoomable
                    nodeStrokeWidth={3}
                />

                <Controls
                    position="bottom-left"
                    showInteractive={true}
                />

                <div
                className="
                absolute
                bottom-4
                right-4
                z-20
                rounded-lg
                border
                bg-white/90
                px-3
                py-2
                text-[11px]
                text-slate-500
                shadow-md
                backdrop-blur
                "
                >
                
                Trading Truth Layer
                <br/>
                Evidence Investigation Canvas

                </div>

                {showLegend && (

                <div
                className="
                absolute
                right-4
                top-4
                z-20
                rounded-xl
                border
                bg-white
                shadow
                p-4
                text-xs
                space-y-2
                "
                >

                <div className="font-semibold mb-3">

                Legend

                </div>

                <div>📄 Claim</div>

                <div># Hash</div>

                <div>📚 Ledger</div>

                <div>📈 Trade</div>

                <div>🏦 Broker</div>

                <div>✔ Verification</div>

                <div>🟧 Trust Tier</div>

                <div>🚨 Integrity Alert</div>

                <div>⚡ Risk</div>

                </div>

                )}

            </ReactFlow>

            </div>

        </div>

    );

}