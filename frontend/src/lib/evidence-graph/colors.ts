export const NODE_COLORS = {

    CLAIM:
        "#2563eb",

    TRADE:
        "#16a34a",

    BROKER_CONNECTION:
        "#15803d",

    BROKER_ACCOUNT:
        "#22c55e",

    IMPORT_BATCH:
        "#06b6d4",

    CSV_IMPORT:
        "#f59e0b",

    REVIEW:
        "#3b82f6",

    DISPUTE:
        "#ea580c",

    AUDIT_EVENT:
        "#7c3aed",

    INTEGRITY_SCAN:
        "#dc2626",

    INTEGRITY_ALERT:
        "#ef4444",

    CLAIM_HASH:
        "#64748b",

    HASH:
        "#64748b",

    FINGERPRINT:
        "#14b8a6",

    TRUST_TIER:
        "#eab308",

    TRADE_SOURCE:
        "#0284c7",

    VERIFICATION:
        "#7c3aed",

    LEDGER:
        "#1e293b",

    RISK:
        "#dc2626",

    METADATA:
        "#94a3b8",

} as const;

export function getNodeColor(

    type?: string,

): string {

    if (!type)
        return "#94a3b8";

    return (

        NODE_COLORS[
            type as keyof typeof NODE_COLORS
        ] ??

        "#94a3b8"

    );

}