import {
    Edge,
    Node,
} from "@xyflow/react";

/*
|--------------------------------------------------------------------------
| Institutional Investigation Layout
|--------------------------------------------------------------------------
*/
import {

    CANVAS,

    GRID,

    NODE,

    LAYERS,

} from "./canvasGeometry";

export const LAYER_SPACING = GRID.COLUMN_SPACING;

export const ROW_SPACING = GRID.ROW_SPACING;

export const NODE_WIDTH = NODE.WIDTH;

export const NODE_HEIGHT = NODE.HEIGHT;

export const LAYER_TITLES = LAYERS;

const LAYER_PADDING = 120;

export function applyInvestigationLayout(
    nodes: Node[],
    edges: Edge[],
): {
    nodes: Node[];
    edges: Edge[];
} {

    const grouped = new Map<number, Node[]>();

    /*
    ------------------------------------------------------------------
    Group nodes by layer
    ------------------------------------------------------------------
    */

    nodes.forEach((node) => {

        const layer = Number(
            (node.data as any)?.layer ?? 0,
        );

        if (!grouped.has(layer)) {
            grouped.set(layer, []);
        }

        grouped.get(layer)!.push(node);

    });

    const positioned: Node[] = [];

    const layers = [...grouped.keys()].sort(
        (a, b) => a - b,
    );

    /*
    ------------------------------------------------------------------
    Position every layer
    ------------------------------------------------------------------
    */

    layers.forEach((layer) => {

        const layerNodes = grouped.get(layer)!;

        const sorted = [...layerNodes].sort(
            (a, b) => {

                const ta = String(
                    (a.data as any)?.type ?? "",
                );

                const tb = String(
                    (b.data as any)?.type ?? "",
                );

                return ta.localeCompare(tb);

            },
        );

        const totalHeight =
            (sorted.length - 1) *
            ROW_SPACING;

        sorted.forEach((node, index) => {

            positioned.push({

                ...node,

                position: {

                    x:

                        (layer - 1) *

                        (

                            NODE_WIDTH +

                            GRID.EDGE_CHANNEL +

                            40

                        ),

                    y:

                        CANVAS.HEIGHT_PADDING +

                        index *

                        ROW_SPACING -

                        totalHeight / 2,

                },

            });

        });

    });

    /*
    ------------------------------------------------------------------
    Simple collision avoidance
    ------------------------------------------------------------------
    */

    const occupied = new Set<string>();

    positioned.forEach((node) => {

        let y = node.position.y;

        while (

            occupied.has(
                `${node.position.x}_${Math.round(y)}`
            )

        ) {

            y += ROW_SPACING;

        }

        node.position.y = y;

        occupied.add(
            `${node.position.x}_${Math.round(y)}`
        );

    });

    /*
    ------------------------------------------------------------------
    Center graph
    ------------------------------------------------------------------
    */

    let minX = Infinity;
    let minY = Infinity;

    positioned.forEach((node) => {

        minX = Math.min(
            minX,
            node.position.x,
        );

        minY = Math.min(
            minY,
            node.position.y,
        );

    });

    positioned.forEach((node) => {

        node.position.x =

            node.position.x -

            minX +

            CANVAS.WIDTH_PADDING;

        node.position.y =

            node.position.y -

            minY +

            CANVAS.HEIGHT_PADDING;

    });

    return {

        nodes: positioned,

        edges,

    };

}

/*
|--------------------------------------------------------------------------
| Investigation Layer Titles
|--------------------------------------------------------------------------
*/
