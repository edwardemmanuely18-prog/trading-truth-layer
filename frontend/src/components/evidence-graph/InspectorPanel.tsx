"use client";

import type {

    EvidenceGraphNode,

    EvidenceGraphResponse,

    EvidenceGraphEdge,

} from "@/lib/evidence-graph/types";

interface Props {

    node: EvidenceGraphNode;

    graph: EvidenceGraphResponse;

    analytics: any;

    graphPath: EvidenceGraphEdge[];

    focusedNodes: EvidenceGraphNode[];

    upstreamEdges: EvidenceGraphEdge[];

    downstreamEdges: EvidenceGraphEdge[];

    selectedNodeEdges: EvidenceGraphEdge[];

    graphDensity: string;

    relationshipTypes: number;

    onClose: () => void;

}

export default function InspectorPanel({

    node,

    graph,

    analytics,

    graphPath,

    focusedNodes,

    upstreamEdges,

    downstreamEdges,

    selectedNodeEdges,

    graphDensity,

    relationshipTypes,

    onClose,

}: Props) {

    return (

        <div className="rounded-2xl border bg-white p-8 mb-8">

            <div className="flex justify-between">

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        INVESTIGATION INSPECTOR

                    </div>

                    <h2 className="mt-2 text-3xl font-bold">

                        {node.label}

                    </h2>

                </div>

                <button

                    onClick={onClose}

                    className="rounded border px-4 py-2"

                >

                    Close

                </button>

            </div>

            <div className="mt-8">

                <div className="grid gap-4 md:grid-cols-4">

                    <Metric

                        title="Focused Nodes"

                        value={focusedNodes.length}

                    />

                    <Metric

                        title="Relationships"

                        value={graphPath.length}

                    />

                    <Metric

                        title="Upstream"

                        value={upstreamEdges.length}

                    />

                    <Metric

                        title="Downstream"

                        value={downstreamEdges.length}

                    />

                </div>

            </div>

            <div className="mt-8 overflow-hidden rounded-xl border">

                <table className="w-full">

                    <tbody>

                        <Row
                            label="Node ID"
                            value={node.id}
                        />

                        <Row
                            label="Node Type"
                            value={node.type}
                        />

                        <Row
                            label="Graph Density"
                            value={graphDensity}
                        />

                        <Row
                            label="Relationship Types"
                            value={relationshipTypes}
                        />

                        <Row
                            label="Evidence Chain"
                            value={graphPath.length}
                        />

                        <Row
                            label="Incoming"
                            value={upstreamEdges.length}
                        />

                        <Row
                            label="Outgoing"
                            value={downstreamEdges.length}
                        />

                    </tbody>

                </table>

            </div>

        </div>

    );

}

function Metric({

    title,

    value,

}:{

    title:string;

    value:number;

}){

    return(

        <div className="rounded-xl border p-4">

            <div className="text-sm text-slate-500">

                {title}

            </div>

            <div className="mt-2 text-3xl font-bold">

                {value}

            </div>

        </div>

    );

}

function Row({

    label,

    value,

}:{

    label:string;

    value:any;

}){

    return(

        <tr className="border-b">

            <td className="bg-slate-50 px-5 py-4 font-medium">

                {label}

            </td>

            <td className="px-5 py-4">

                {value}

            </td>

        </tr>

    );

}