"use client";

import {
    memo,
} from "react";

import {
    Handle,
    Position,
    NodeProps,
} from "@xyflow/react";

import {

    NODE,

} from "@/lib/evidence-graph/canvasGeometry";


interface InvestigationData {

    id: string;

    label: string;

    type: string;

    layer: number;

    color: string;

    metadata?: Record<
        string,
        unknown
    >;

}

const ICONS: Record<
    string,
    string
> = {

    CLAIM: "📄",

    TRADE: "📈",

    BROKER_CONNECTION: "🔗",

    BROKER_ACCOUNT: "🏦",

    IMPORT_BATCH: "📦",

    CSV_IMPORT: "📑",

    AUDIT_EVENT: "📝",

    REVIEW: "✔",

    DISPUTE: "⚠",

    INTEGRITY_SCAN: "🛡",

    INTEGRITY_ALERT: "🚨",

    CLAIM_HASH: "#",

    RISK: "⚡",

    METADATA: "ℹ",

};

function InvestigationNode({

    data,

    selected,

}: NodeProps) {

    const node = data as unknown as InvestigationData;

    const entries =
        Object.entries(
            node.metadata ?? {},
        );

    return (

        <>

            <Handle
                type="target"
                position={Position.Left}
            />

            <div

                className={`
                    style={{

                        width: NODE.WIDTH,

                        minHeight: NODE.HEIGHT,

                    }}
                    rounded-xl
                    border
                    bg-white
                    shadow-sm
                    transition-all
                    duration-200
                    ${
                        selected
                            ? "ring-2 ring-blue-500 shadow-lg"
                            : ""
                    }
                `}

            >

                <div

                    className="
                        flex
                        items-center
                        gap-3
                        rounded-t-xl
                        px-4
                        py-3
                        text-white
                    "

                    style={{

                        background:
                            node.color,

                    }}

                >

                    <div className="text-lg">

                        {ICONS[
                            node.type
                        ] ?? "●"}

                    </div>

                    <div>

                        {node.type === "CLAIM" && (

                            <div
                                className="
                                    inline-flex
                                    items-center
                                    rounded-md
                                    bg-white/20
                                    px-2
                                    py-1
                                    mb-2
                                    text-[10px]
                                    font-bold
                                    uppercase
                                    tracking-wide
                                "
                            >
                                ROOT INVESTIGATION
                            </div>

                        )}

                        <div className="text-xs opacity-80">

                            {node.type}

                        </div>

                        <div className="font-semibold text-base">

                            {node.label}

                        </div>

                        <div
                            className="
                                mt-2
                                inline-flex
                                rounded-md
                                bg-slate-100
                                px-2
                                py-1
                                text-[10px]
                                font-semibold
                                uppercase
                                tracking-wide
                            "
                        >
                            Layer {node.layer}
                        </div>

                    </div>

                </div>

                <div className="p-4 space-y-2">

                    <Row
                        title="ID"
                        value={node.id}
                    />

                    <Row
                        title="Layer"
                        value={String(
                            node.layer,
                        )}
                    />

                    {entries
                        .filter((entry) => {
                            const value = entry[1];

                            return (
                                value !== null &&
                                value !== "" &&
                                value !== undefined
                            );
                        })
                        .slice(0, 5)
                        .map(([k, v]) => (
                            <Row
                                key={k}
                                title={k}
                                value={String(v)}
                            />
                        ))}

                        {entries.length > 5 && (
                            <div className="pt-2 text-center">
                                <span
                                    className="
                                        rounded
                                        bg-slate-100
                                        px-2
                                        py-1
                                        text-[10px]
                                        font-medium
                                        text-slate-500
                                    "
                                >
                                    + {entries.length - 5} more fields
                                </span>
                            </div>
                        )}

                </div>

            </div>

            <Handle
                type="source"
                position={Position.Right}
            />

        </>

    );

}

interface RowProps {

    title: string;

    value: string;

}

function Row({

    title,

    value,

}: RowProps) {

    return (

        <div className="flex justify-between gap-3">

            <div className="text-xs text-slate-500">

                {title}

            </div>

            <div className="text-xs font-medium text-right break-all">

                {value}

            </div>

        </div>

    );

}

export default memo(
    InvestigationNode,
);