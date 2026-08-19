"use client";

import {
    useEffect,
    useMemo,
    useState,
} from "react";

import { RefreshCw } from "lucide-react";

import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
    api,
    type AuditEvent,
    type V2EvidenceRegistryRecord,
    type V2EvidenceRegistrySummary,
} from "../../../../lib/api";

type AuditTab =
    | "AUDIT_TIMELINE"
    | "INTEGRITY_REGISTRY"
    | "CHAIN_OF_CUSTODY"
    | "DIGITAL_SIGNATURES"
    | "VERIFICATION_EVENTS";

const TABS: Array<{
    key: AuditTab;
    label: string;
}> = [
    {
        key: "AUDIT_TIMELINE",
        label: "Audit Timeline",
    },
    {
        key: "INTEGRITY_REGISTRY",
        label: "Integrity Registry",
    },
    {
        key: "CHAIN_OF_CUSTODY",
        label: "Chain of Custody",
    },
    {
        key: "DIGITAL_SIGNATURES",
        label: "Digital Signatures",
    },
    {
        key: "VERIFICATION_EVENTS",
        label: "Verification Events",
    },
];

function displayValue(
    value: unknown,
): string {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "—";
    }

    return String(value);
}

function formatDate(
    value: string | null | undefined,
): string {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return new Intl.DateTimeFormat(
        "en-GB",
        {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            timeZoneName: "short",
            hour12: false,
        },
    ).format(date);
}

function auditField(
    event: AuditEvent,
    key: string,
): unknown {
    return (
        event as unknown as Record<
            string,
            unknown
        >
    )[key];
}

function parseAuditObject(
    value: unknown,
): Record<string, unknown> | null {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return null;
    }

    if (
        typeof value === "object" &&
        !Array.isArray(value)
    ) {
        return value as Record<string, unknown>;
    }

    if (typeof value !== "string") {
        return null;
    }

    try {
        const parsed = JSON.parse(value);

        if (
            parsed &&
            typeof parsed === "object" &&
            !Array.isArray(parsed)
        ) {
            return parsed as Record<
                string,
                unknown
            >;
        }
    } catch {
        return null;
    }

    return null;
}

function humanizeAuditKey(
    key: string,
): string {
    return key
        .replace(/_/g, " ")
        .replace(/\b\w/g, (letter) =>
            letter.toUpperCase()
        );
}

function formatAuditObjectValue(
    key: string,
    value: unknown,
): string {
    if (
        value === null ||
        value === undefined
    ) {
        return "—";
    }

    if (
        typeof value === "boolean"
    ) {
        return value ? "Yes" : "No";
    }

    if (
        typeof value === "object"
    ) {
        return JSON.stringify(
            value,
        );
    }

    const text = String(value);

    const looksLikeHash =
        key.toLowerCase().includes("hash");

    if (
        looksLikeHash &&
        text.length > 32
    ) {
        return `${text.slice(0, 20)}…${text.slice(-8)}`;
    }

    return text;
}

function resolveAuditActor(
    event: AuditEvent,
): string {
    const directActor =
        auditField(
            event,
            "actor_id",
        );

    if (
        directActor !== null &&
        directActor !== undefined &&
        String(directActor).trim() !== ""
    ) {
        return String(
            directActor,
        );
    }

    const metadata =
        parseAuditObject(
            auditField(
                event,
                "metadata_json",
            ),
        );

    const metadataActor =
        metadata?.actor_user_id ??
        metadata?.actor_id ??
        metadata?.user_id;

    if (
        metadataActor !== null &&
        metadataActor !== undefined &&
        String(metadataActor).trim() !== ""
    ) {
        return `User #${metadataActor}`;
    }

    return "System / Unattributed";
}

function AuditObjectPanel({
    label,
    value,
}: {
    label: string;
    value: unknown;
}) {
    const parsed =
        parseAuditObject(
            value,
        );

    if (!parsed) {
        return (
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    {label}
                </div>

                <div className="mt-2 break-words text-sm text-slate-700">
                    {displayValue(
                        value,
                    )}
                </div>
            </div>
        );
    }

    const entries =
        Object.entries(parsed);

    if (entries.length === 0) {
        return (
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    {label}
                </div>

                <div className="mt-2 text-sm text-slate-500">
                    No recorded values.
                </div>
            </div>
        );
    }

    return (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
            <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                {label}
            </div>

            <div className="mt-3 space-y-2">
                {entries.map(
                    ([key, entryValue]) => (
                        <div
                            key={key}
                            className="flex flex-col gap-1 border-b border-slate-200 pb-2 last:border-b-0 last:pb-0 sm:flex-row sm:items-start sm:justify-between sm:gap-6"
                        >
                            <div className="text-xs font-medium text-slate-500">
                                {humanizeAuditKey(
                                    key,
                                )}
                            </div>

                            <div
                                className="break-words text-right text-sm font-medium text-slate-800"
                                title={
                                    typeof entryValue ===
                                    "string"
                                        ? entryValue
                                        : undefined
                                }
                            >
                                {formatAuditObjectValue(
                                    key,
                                    entryValue,
                                )}
                            </div>
                        </div>
                    ),
                )}
            </div>
        </div>
    );
}

export default function AuditIntegrityPage() {
    const params = useParams<{
        workspaceId: string;
    }>();

    const workspaceId = Number(
        params.workspaceId,
    );

    const [
        activeTab,
        setActiveTab,
    ] = useState<AuditTab>(
        "AUDIT_TIMELINE",
    );

    const [
        auditEvents,
        setAuditEvents,
    ] = useState<AuditEvent[]>(
        [],
    );

    const [
        evidenceRecords,
        setEvidenceRecords,
    ] = useState<
        V2EvidenceRegistryRecord[]
    >([]);

    const [
        summary,
        setSummary,
    ] = useState<
        V2EvidenceRegistrySummary | null
    >(null);

    const [
        loading,
        setLoading,
    ] = useState(true);

    const [
        error,
        setError,
    ] = useState<string | null>(
        null,
    );

    async function loadAuditIntegrity() {
        try {
            setLoading(true);
            setError(null);

            const [
                eventsResponse,
                evidenceResponse,
                summaryResponse,
            ] = await Promise.all([
                api.getAuditEventsForWorkspace(
                    workspaceId,
                    50,
                ),

                api.getV2EvidenceRegistryPage(
                    workspaceId,
                    1,
                    50,
                ),

                api.getV2EvidenceRegistrySummary(
                    workspaceId,
                ),
            ]);

            setAuditEvents(
                Array.isArray(
                    eventsResponse,
                )
                    ? eventsResponse
                    : [],
            );

            setEvidenceRecords(
                evidenceResponse.records,
            );

            setSummary(
                summaryResponse,
            );
        } catch (err) {
            console.error(err);

            setError(
                err instanceof Error
                    ? err.message
                    : "Unable to load audit and integrity data.",
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (
            !Number.isFinite(
                workspaceId,
            )
        ) {
            setError(
                "Invalid workspace ID.",
            );

            setLoading(false);
            return;
        }

        void loadAuditIntegrity();
    }, [workspaceId]);

    const verificationEvents =
        useMemo(() => {
            return auditEvents.filter(
                (event) => {
                    const eventType =
                        displayValue(
                            auditField(
                                event,
                                "event_type",
                            ),
                        ).toLowerCase();

                    const metadata =
                        displayValue(
                            auditField(
                                event,
                                "metadata_json",
                            ),
                        ).toLowerCase();

                    return (
                        eventType.includes(
                            "verif",
                        ) ||
                        metadata.includes(
                            "verif",
                        )
                    );
                },
            );
        }, [auditEvents]);

    const activeTabLabel =
        TABS.find(
            (tab) =>
                tab.key ===
                activeTab,
        )?.label ?? "Audit & Integrity";

    const integrityCount =
        summary?.total_records ?? 0;

    const auditCount =
        auditEvents.length;

    const verificationCount =
        verificationEvents.length;

    return (
        <div className="min-h-screen bg-slate-50">
            <Navbar
                workspaceId={
                    workspaceId
                }
            />

            <main className="mx-auto max-w-7xl px-6 py-10">

                <div className="mb-8">
                    <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Evidence Registry
                    </div>

                    <div className="mt-2 flex items-center justify-between gap-6">
                        <div>
                            <h1 className="text-4xl font-bold text-slate-950">
                                Audit & Integrity
                            </h1>

                            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                                Governance workspace for audit history,
                                evidence integrity, chain of custody,
                                signatures, and verification events.
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={() =>
                                void loadAuditIntegrity()
                            }
                            disabled={loading}
                            className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <RefreshCw
                                className={
                                    loading
                                        ? "h-4 w-4 animate-spin"
                                        : "h-4 w-4"
                                }
                            />

                            Refresh
                        </button>
                    </div>
                </div>

                {error && (
                    <section className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-5 py-4">
                        <div className="text-sm font-semibold text-red-800">
                            Audit & Integrity unavailable
                        </div>

                        <div className="mt-1 text-sm text-red-700">
                            {error}
                        </div>
                    </section>
                )}

                <section className="mb-6 grid gap-4 md:grid-cols-3">

                    <div className="rounded-2xl border border-slate-300 bg-white p-5 shadow-sm">
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                            Audit Events Loaded
                        </div>

                        <div className="mt-2 text-3xl font-bold text-slate-950">
                            {auditCount.toLocaleString()}
                        </div>

                        <div className="mt-1 text-xs text-slate-500">
                            Latest workspace events
                        </div>
                    </div>

                    <div className="rounded-2xl border border-slate-300 bg-white p-5 shadow-sm">
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                            Canonical Evidence
                        </div>

                        <div className="mt-2 text-3xl font-bold text-slate-950">
                            {integrityCount.toLocaleString()}
                        </div>

                        <div className="mt-1 text-xs text-slate-500">
                            Records in the durable V2 registry
                        </div>
                    </div>

                    <div className="rounded-2xl border border-slate-300 bg-white p-5 shadow-sm">
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                            Verification Events
                        </div>

                        <div className="mt-2 text-3xl font-bold text-slate-950">
                            {verificationCount.toLocaleString()}
                        </div>

                        <div className="mt-1 text-xs text-slate-500">
                            Matching recent audit events
                        </div>
                    </div>

                </section>

                <section className="overflow-hidden rounded-2xl border border-slate-300 bg-white shadow-sm">

                    <div className="border-b border-slate-200 px-6 pt-5">
                        <div className="flex flex-wrap gap-2">
                            {TABS.map(
                                (
                                    tab,
                                ) => {
                                    const active =
                                        activeTab ===
                                        tab.key;

                                    let count = 0;

                                    if (
                                        tab.key ===
                                        "AUDIT_TIMELINE"
                                    ) {
                                        count =
                                            auditCount;
                                    } else if (
                                        tab.key ===
                                        "INTEGRITY_REGISTRY"
                                    ) {
                                        count =
                                            integrityCount;
                                    } else if (
                                        tab.key ===
                                        "CHAIN_OF_CUSTODY"
                                    ) {
                                        count =
                                            evidenceRecords.length;
                                    } else if (
                                        tab.key ===
                                        "VERIFICATION_EVENTS"
                                    ) {
                                        count =
                                            verificationCount;
                                    }

                                    return (
                                        <button
                                            key={
                                                tab.key
                                            }
                                            type="button"
                                            onClick={() =>
                                                setActiveTab(
                                                    tab.key,
                                                )
                                            }
                                            className={[
                                                "rounded-lg px-4 py-2 text-sm font-semibold transition",
                                                active
                                                    ? "bg-slate-950 text-white"
                                                    : "border border-slate-200 text-slate-600 hover:bg-slate-50",
                                            ].join(
                                                " ",
                                            )}
                                        >
                                            {
                                                tab.label
                                            }

                                            <span
                                                className={[
                                                    "ml-2 rounded-full px-2 py-0.5 text-[10px]",
                                                    active
                                                        ? "bg-white/15 text-white"
                                                        : "bg-slate-100 text-slate-500",
                                                ].join(
                                                    " ",
                                                )}
                                            >
                                                {count}
                                            </span>
                                        </button>
                                    );
                                },
                            )}
                        </div>
                    </div>

                    <div className="px-6 py-7">

                        <div className="mb-5">
                            <div className="text-sm font-semibold text-slate-950">
                                {
                                    activeTabLabel
                                }
                            </div>
                        </div>

                        {loading ? (
                            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-16 text-center">
                                <RefreshCw className="mx-auto h-5 w-5 animate-spin text-slate-400" />

                                <div className="mt-3 text-sm text-slate-600">
                                    Loading governance data...
                                </div>
                            </div>
                        ) : (
                            <>
                                {activeTab ===
                                    "AUDIT_TIMELINE" && (
                                    <div className="space-y-3">
                                        {auditEvents.length ===
                                        0 ? (
                                            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-14 text-center text-sm text-slate-500">
                                                No workspace audit events
                                                were returned.
                                            </div>
                                        ) : (
                                            auditEvents.map(
                                                (
                                                    event,
                                                    index,
                                                ) => (
                                                    <div
                                                        key={
                                                            String(
                                                                auditField(
                                                                    event,
                                                                    "id",
                                                                ) ??
                                                                    index,
                                                            )
                                                        }
                                                        className="rounded-xl border border-slate-200 bg-white p-4"
                                                    >
                                                        <div className="flex flex-wrap items-start justify-between gap-4">
                                                            <div>
                                                                <div className="font-semibold text-slate-900">
                                                                    {displayValue(
                                                                        auditField(
                                                                            event,
                                                                            "event_type",
                                                                        ),
                                                                    )}
                                                                </div>

                                                                <div className="mt-1 text-xs text-slate-500">
                                                                    {displayValue(
                                                                        auditField(
                                                                            event,
                                                                            "entity_type",
                                                                        ),
                                                                    )}
                                                                    {" · "}
                                                                    {displayValue(
                                                                        auditField(
                                                                            event,
                                                                            "entity_id",
                                                                        ),
                                                                    )}
                                                                </div>
                                                            </div>

                                                            <div className="text-right text-xs text-slate-500">
                                                                {formatDate(
                                                                    displayValue(
                                                                        auditField(
                                                                            event,
                                                                            "created_at",
                                                                        ),
                                                                    ),
                                                                )}
                                                            </div>
                                                        </div>

                                                        <div className="mt-3 grid gap-3 md:grid-cols-3">
                                                            <div>
                                                                <div className="text-[10px] uppercase tracking-wider text-slate-400">
                                                                    Actor
                                                                </div>

                                                                <div className="mt-1 text-sm text-slate-700">
                                                                    {resolveAuditActor(event)}
                                                                </div>
                                                            </div>

                                                            <div>
                                                                <div className="text-[10px] uppercase tracking-wider text-slate-400">
                                                                    Entity
                                                                </div>

                                                                <div className="mt-1 text-sm text-slate-700">
                                                                    {displayValue(
                                                                        auditField(
                                                                            event,
                                                                            "entity_type",
                                                                        ),
                                                                    )}
                                                                    {" · "}
                                                                    {displayValue(
                                                                        auditField(
                                                                            event,
                                                                            "entity_id",
                                                                        ),
                                                                    )}
                                                                </div>
                                                            </div>

                                                            <div>
                                                                <div className="text-[10px] uppercase tracking-wider text-slate-400">
                                                                    Workspace
                                                                </div>

                                                                <div className="mt-1 text-sm text-slate-700">
                                                                    {displayValue(
                                                                        auditField(
                                                                            event,
                                                                            "workspace_id",
                                                                        ),
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <div className="mt-4 grid gap-3 md:grid-cols-2">
                                                            <AuditObjectPanel
                                                                label="Previous State"
                                                                value={auditField(
                                                                    event,
                                                                    "old_state",
                                                                )}
                                                            />

                                                            <AuditObjectPanel
                                                                label="New State"
                                                                value={auditField(
                                                                    event,
                                                                    "new_state",
                                                                )}
                                                            />
                                                        </div>

                                                        {displayValue(
                                                            auditField(
                                                                event,
                                                                "metadata_json",
                                                            ),
                                                        ) !== "—" && (
                                                            <details className="mt-3 rounded-lg border border-slate-200 bg-slate-50">
                                                                <summary className="cursor-pointer px-3 py-2 text-xs font-semibold text-slate-600">
                                                                    Event Metadata
                                                                </summary>

                                                                <div className="border-t border-slate-200 p-3">
                                                                    <AuditObjectPanel
                                                                        label="Metadata"
                                                                        value={auditField(
                                                                            event,
                                                                            "metadata_json",
                                                                        )}
                                                                    />
                                                                </div>
                                                            </details>
                                                        )}
                                                    </div>
                                                ),
                                            )
                                        )}
                                    </div>
                                )}

                                {activeTab ===
                                    "INTEGRITY_REGISTRY" && (
                                    <div className="overflow-x-auto rounded-xl border border-slate-200">
                                        <table className="min-w-full">
                                            <thead className="bg-slate-50">
                                                <tr className="border-b border-slate-200">
                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                        Evidence
                                                    </th>

                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                        Type
                                                    </th>

                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                        Evidence Hash
                                                    </th>

                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                        Version
                                                    </th>

                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                        Lifecycle
                                                    </th>
                                                </tr>
                                            </thead>

                                            <tbody>
                                                {evidenceRecords.map(
                                                    (
                                                        record,
                                                    ) => (
                                                        <tr
                                                            key={
                                                                record.canonical_evidence_id
                                                            }
                                                            className="border-b border-slate-100 hover:bg-slate-50"
                                                        >
                                                            <td className="px-5 py-4">
                                                                <a
                                                                    href={`/workspace/${workspaceId}/evidence-explorer/${encodeURIComponent(
                                                                        record.canonical_evidence_id,
                                                                    )}`}
                                                                    className="font-mono text-xs font-semibold text-slate-900 hover:text-blue-700 hover:underline"
                                                                >
                                                                    {
                                                                        record.canonical_evidence_id
                                                                    }
                                                                </a>
                                                            </td>

                                                            <td className="px-5 py-4">
                                                                <span className="rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700">
                                                                    {
                                                                        record.evidence_type
                                                                    }
                                                                </span>
                                                            </td>

                                                            <td className="max-w-sm break-all px-5 py-4 font-mono text-[11px] text-slate-600">
                                                                {
                                                                    record.evidence_hash
                                                                }
                                                            </td>

                                                            <td className="px-5 py-4 text-sm text-slate-700">
                                                                {
                                                                    record.evidence_version
                                                                }
                                                            </td>

                                                            <td className="px-5 py-4">
                                                                <span className="rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700">
                                                                    {
                                                                        record.lifecycle
                                                                    }
                                                                </span>
                                                            </td>
                                                        </tr>
                                                    ),
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                )}

                                {activeTab ===
                                    "CHAIN_OF_CUSTODY" && (
                                    <div className="overflow-x-auto rounded-xl border border-slate-200">
                                        <table className="min-w-full">
                                            <thead className="bg-slate-50">
                                                <tr className="border-b border-slate-200">
                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                        Evidence
                                                    </th>

                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                        Session
                                                    </th>

                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                        Batch
                                                    </th>

                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                        Provider
                                                    </th>

                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                        Registered
                                                    </th>
                                                </tr>
                                            </thead>

                                            <tbody>
                                                {evidenceRecords.map(
                                                    (
                                                        record,
                                                    ) => (
                                                        <tr
                                                            key={
                                                                record.canonical_evidence_id
                                                            }
                                                            className="border-b border-slate-100"
                                                        >
                                                            <td className="px-5 py-4 font-mono text-xs text-slate-800">
                                                                {
                                                                    record.canonical_evidence_id
                                                                }
                                                            </td>

                                                            <td className="max-w-xs break-all px-5 py-4 font-mono text-[11px] text-slate-600">
                                                                {displayValue(
                                                                    record.synchronization_session,
                                                                )}
                                                            </td>

                                                            <td className="max-w-xs break-all px-5 py-4 font-mono text-[11px] text-slate-600">
                                                                {displayValue(
                                                                    record.synchronization_batch,
                                                                )}
                                                            </td>

                                                            <td className="px-5 py-4">
                                                                <div className="text-sm font-semibold text-slate-900">
                                                                    {
                                                                        record.provider
                                                                            .provider_name
                                                                    }
                                                                </div>

                                                                <div className="mt-1 text-xs text-slate-500">
                                                                    {
                                                                        record.provider
                                                                            .provider_platform
                                                                    }
                                                                </div>
                                                            </td>

                                                            <td className="whitespace-nowrap px-5 py-4 text-xs text-slate-600">
                                                                {formatDate(
                                                                    record.registered_at,
                                                                )}
                                                            </td>
                                                        </tr>
                                                    ),
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                )}

                                {activeTab ===
                                    "DIGITAL_SIGNATURES" && (
                                    <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-16 text-center">
                                        <div className="text-sm font-semibold text-slate-900">
                                            No dedicated V2 digital-signature registry is currently exposed.
                                        </div>

                                        <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                                            This surface is intentionally not
                                            synthesizing signature records from
                                            hashes. When the signature contract
                                            is introduced, this tab can consume
                                            it directly.
                                        </p>
                                    </div>
                                )}

                                {activeTab ===
                                    "VERIFICATION_EVENTS" && (
                                    <div className="space-y-3">
                                        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
                                            Showing recent workspace audit events
                                            whose existing event fields indicate
                                            verification activity.
                                        </div>

                                        {verificationEvents.length ===
                                        0 ? (
                                            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-14 text-center text-sm text-slate-500">
                                                No matching verification audit
                                                events were returned.
                                            </div>
                                        ) : (
                                            verificationEvents.map(
                                                (
                                                    event,
                                                    index,
                                                ) => (
                                                    <div
                                                        key={
                                                            String(
                                                                auditField(
                                                                    event,
                                                                    "id",
                                                                ) ??
                                                                    index,
                                                            )
                                                        }
                                                        className="rounded-xl border border-slate-200 p-4"
                                                    >
                                                        <div className="flex items-start justify-between gap-4">
                                                            <div>
                                                                <div className="text-sm font-semibold text-slate-900">
                                                                    {
                                                                        displayValue(
                                                                            auditField(
                                                                                event,
                                                                                "event_type",
                                                                            ),
                                                                        )
                                                                    }
                                                                </div>

                                                                <div className="mt-1 text-xs text-slate-500">
                                                                    {
                                                                        displayValue(
                                                                            auditField(
                                                                                event,
                                                                                "entity_type",
                                                                            ),
                                                                        )
                                                                    }
                                                                    {" · "}
                                                                    {
                                                                        displayValue(
                                                                            auditField(
                                                                                event,
                                                                                "entity_id",
                                                                            ),
                                                                        )
                                                                    }
                                                                </div>
                                                            </div>

                                                            <div className="text-xs text-slate-500">
                                                                {formatDate(
                                                                    displayValue(
                                                                        auditField(
                                                                            event,
                                                                            "created_at",
                                                                        ),
                                                                    ),
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                ),
                                            )
                                        )}
                                    </div>
                                )}

                            </>
                        )}
                    </div>
                </section>

            </main>
        </div>
    );
}