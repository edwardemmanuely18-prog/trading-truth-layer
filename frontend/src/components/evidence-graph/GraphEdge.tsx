"use client";

import {
    BaseEdge,
    EdgeLabelRenderer,
    EdgeProps,
    MarkerType,
    getBezierPath,
} from "@xyflow/react";

const EDGE_COLOURS: Record<string, string> = {

    HAS_HASH: "#64748B",

    CONTAINS: "#94A3B8",

    VERIFIED_BY: "#0EA5E9",

    GENERATED_FROM: "#F59E0B",

    HAS_TIER: "#8B5CF6",

    SUPPORTED_BY: "#10B981",

    HAS_RISK: "#EF4444",

};

export default function GraphEdge({

    id,

    sourceX,

    sourceY,

    targetX,

    targetY,

    sourcePosition,

    targetPosition,

    data,

}: EdgeProps) {

    const relationship = String(

        data?.relationship ?? ""

    );

    const colour =

        EDGE_COLOURS[relationship] ??

        "#64748B";

    const [

        path,

        labelX,

        labelY,

    ] = getBezierPath({

        sourceX,

        sourceY,

        targetX,

        targetY,

        sourcePosition,

        targetPosition,

        curvature: 0.22,

    });

    const distance = Math.sqrt(

        Math.pow(targetX - sourceX, 2) +

        Math.pow(targetY - sourceY, 2)

    );

    const showLabel =

        distance > 170;

    const critical =

        relationship ===

        "CRITICAL_PATH";

    return (

        <>

            <BaseEdge

                id={id}

                path={path}

                markerEnd={MarkerType.ArrowClosed}

                style={{

                    stroke: colour,

                    strokeWidth: critical ? 3 : 1.6,

                    strokeDasharray: critical

                        ? "8 4"

                        : undefined,

                    animation: critical

                        ? "dashdraw 12s linear infinite"

                        : undefined,

                }}

            />

            {showLabel && (

                <EdgeLabelRenderer>

                    <div

                        style={{

                            position: "absolute",

                            transform:

                                `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,

                            background: "rgba(255,255,255,.96)",

                            border:

                                `1px solid ${colour}`,

                            borderRadius: 999,

                            padding:

                                "2px 6px",

                            fontSize: 10,

                            fontWeight: 600,

                            color: colour,

                            whiteSpace: "nowrap",

                            boxShadow:

                                "0 1px 4px rgba(0,0,0,.08)",

                            pointerEvents: "none",

                        }}

                    >

                        {relationship

                            .replaceAll("_", " ")}

                    </div>

                </EdgeLabelRenderer>

            )}

        </>

    );

}