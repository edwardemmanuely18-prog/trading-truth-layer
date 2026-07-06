/*
|--------------------------------------------------------------------------
| Evidence Graph Geometry
|--------------------------------------------------------------------------
| Single source of truth for Investigation Canvas dimensions.
| Every component (layout, canvas, nodes) imports from here.
|--------------------------------------------------------------------------
*/

export const CANVAS = {

    WIDTH_PADDING: 80,

    HEIGHT_PADDING: 80,

    HEADER_HEIGHT: 72,

    TOOLBAR_HEIGHT: 56,

    LEGEND_WIDTH: 180,

};

export const NODE = {

    WIDTH: 280,

    HEIGHT: 210,

    HEADER_HEIGHT: 82,

    BODY_PADDING: 16,

    BORDER_RADIUS: 14,

};

export const GRID = {

    COLUMN_SPACING: 430,

    ROW_SPACING: 250,

    EDGE_CHANNEL: 110,

};

export const VIEWPORT = {

    FIT_PADDING: 0.20,

    MIN_ZOOM: 0.15,

    MAX_ZOOM: 3,

};

export const LAYERS = [

    "CLAIM",

    "EVIDENCE",

    "TRADE LEDGER",

    "PROVENANCE",

    "INFRASTRUCTURE",

    "GOVERNANCE",

    "RISK & TRUST",

];