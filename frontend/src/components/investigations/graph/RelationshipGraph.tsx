"use client";

import type {
    InvestigationNode,
    InvestigationRelationship,
} from "@/lib/api";

import SectionCard from "../common/SectionCard";

interface Props {

    nodes: InvestigationNode[];

    relationships: InvestigationRelationship[];

}

function plural(
    value: number,
    singular: string,
    pluralWord: string,
) {

    return value === 1
        ? singular
        : pluralWord;

}

export default function RelationshipGraph({

    nodes,

    relationships,

}: Props) {

    const nodeTypes = new Map<string, number>();

    for (const node of nodes) {

        nodeTypes.set(

            node.node_type,

            (nodeTypes.get(node.node_type) ?? 0) + 1,

        );

    }

    const relationshipTypes = new Map<string, number>();

    for (const edge of relationships) {

        relationshipTypes.set(

            edge.relationship,

            (relationshipTypes.get(edge.relationship) ?? 0) + 1,

        );

    }

    const density =

        nodes.length === 0

            ? 0

            : relationships.length / nodes.length;

    return (

        <SectionCard

            title="Institutional Investigation Graph"

            subtitle="Canonical entity relationships reconstructed by IIS"

        >

            <div className="space-y-8">

                {/* ===================================================== */}
                {/* Graph Statistics */}
                {/* ===================================================== */}

                <div className="grid gap-4 md:grid-cols-4">

                    <div className="rounded-lg border bg-slate-50 p-5">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Nodes

                        </div>

                        <div className="mt-2 text-4xl font-bold">

                            {nodes.length}

                        </div>

                    </div>

                    <div className="rounded-lg border bg-slate-50 p-5">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Relationships

                        </div>

                        <div className="mt-2 text-4xl font-bold">

                            {relationships.length}

                        </div>

                    </div>

                    <div className="rounded-lg border bg-slate-50 p-5">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Entity Types

                        </div>

                        <div className="mt-2 text-4xl font-bold">

                            {nodeTypes.size}

                        </div>

                    </div>

                    <div className="rounded-lg border bg-slate-50 p-5">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Graph Density

                        </div>

                        <div className="mt-2 text-4xl font-bold">

                            {density.toFixed(2)}

                        </div>

                    </div>

                </div>

                {/* ===================================================== */}
                {/* Entity Inventory */}
                {/* ===================================================== */}

                <div>

                    <div className="mb-4 text-xs uppercase tracking-widest text-slate-500">

                        Investigation Entities

                    </div>

                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

                        {[...nodeTypes.entries()].map(

                            ([type, count]) => (

                                <div

                                    key={type}

                                    className="rounded-lg border bg-white p-4"

                                >

                                    <div className="font-semibold">

                                        {type}

                                    </div>

                                    <div className="mt-2 text-3xl font-bold">

                                        {count}

                                    </div>

                                    <div className="mt-1 text-sm text-slate-500">

                                        {plural(

                                            count,

                                            "entity",

                                            "entities",

                                        )}

                                    </div>

                                </div>

                            ),

                        )}

                    </div>

                </div>

                {/* ===================================================== */}
                {/* Relationship Inventory */}
                {/* ===================================================== */}

                <div>

                    <div className="mb-4 text-xs uppercase tracking-widest text-slate-500">

                        Relationship Types

                    </div>

                    <div className="max-h-72 overflow-y-auto rounded-lg border">

                        <table className="min-w-full">

                            <thead className="sticky top-0 bg-white z-10">

                                <tr className="border-b">

                                    <th className="px-4 py-3 text-left">

                                        Relationship

                                    </th>

                                    <th className="px-4 py-3 text-right">

                                        Count

                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                {[...relationshipTypes.entries()].map(

                                    ([type, count]) => (

                                        <tr

                                            key={type}

                                            className="border-b"

                                        >

                                            <td className="px-4 py-3">

                                                {type}

                                            </td>

                                            <td className="px-4 py-3 text-right font-semibold">

                                                {count}

                                            </td>

                                        </tr>

                                    ),

                                )}

                            </tbody>

                        </table>

                    </div>

                </div>

                {/* ===================================================== */}
                {/* Node Preview */}
                {/* ===================================================== */}

                <div>

                    <div className="mb-4 text-xs uppercase tracking-widest text-slate-500">

                        Investigation Nodes

                    </div>

                    <div className="max-h-96 overflow-y-auto rounded-lg border">

                        <table className="min-w-full">

                            <thead className="sticky top-0 bg-white z-10">

                                <tr className="border-b">

                                    <th className="px-4 py-3 text-left">

                                        Label

                                    </th>

                                    <th className="px-4 py-3 text-left">

                                        Type

                                    </th>

                                    <th className="px-4 py-3 text-right">

                                        Node ID

                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                {nodes.map((node) => (

                                    <tr
                                        key={node.id}
                                        className="border-b"
                                    >

                                        <td className="px-4 py-3 font-medium">

                                            {node.label}

                                        </td>

                                        <td className="px-4 py-3 text-slate-600">

                                            {node.node_type}

                                        </td>

                                        <td className="px-4 py-3 text-right font-mono text-xs">

                                            {node.id}

                                        </td>

                                    </tr>

                                ))}

                            </tbody>

                        </table>

                    </div>

                </div>

                {/* ===================================================== */}
                {/* Institutional Interpretation */}
                {/* ===================================================== */}

                <div className="rounded-lg border bg-slate-50 p-6">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Institutional Interpretation

                    </div>

                    <div className="mt-3 leading-7 text-slate-700">

                        The Investigation Graph is the canonical
                        structural representation produced by the
                        Institutional Investigation System. Every
                        investigation domain contributes entities
                        and relationships to this graph, allowing
                        IIS to reconstruct how execution,
                        verification, governance, evidence,
                        synchronization, broker activity and review
                        history are connected before producing the
                        final allocator decision.

                    </div>

                </div>

            </div>

        </SectionCard>

    );

}