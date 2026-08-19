"use client";

import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    RefreshCw,
} from "lucide-react";

import {
    useParams,
} from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
    api,
    type V2EvidenceRegistryRecord,
    type V2EvidenceRegistrySummary,
} from "../../../../lib/api";

type SystemTab =
    | "TERMINAL"
    | "EXPERT_ADVISORS"
    | "INDICATORS"
    | "SCRIPTS"
    | "LOGS"
    | "CONFIGURATION"
    | "CHARTS";

const TABS: Array<{
    key: SystemTab;
    label: string;
}> = [
    {
        key: "TERMINAL",
        label: "Terminal",
    },
    {
        key: "EXPERT_ADVISORS",
        label: "Expert Advisors",
    },
    {
        key: "INDICATORS",
        label: "Indicators",
    },
    {
        key: "SCRIPTS",
        label: "Scripts",
    },
    {
        key: "LOGS",
        label: "Logs",
    },
    {
        key: "CONFIGURATION",
        label: "Configuration",
    },
    {
        key: "CHARTS",
        label: "Charts",
    },
];

function displayValue(
    value: unknown
) {
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
    value: string | null
) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}

function getRecordMetadataValue(
    record: V2EvidenceRegistryRecord,
    key: string
) {
    return record.metadata?.[
        key
    ];
}

function isTerminalRecord(
    record: V2EvidenceRegistryRecord
) {
    const metadata = record.metadata ?? {};

    const values = [
        metadata.evidence_category,
        metadata.category,
        metadata.system_category,
        metadata.source_category,
        metadata.object_type,
        metadata.native_object_type,
    ]
        .filter(
            (
                value
            ) =>
                value !== null &&
                value !== undefined &&
                value !== ""
        )
        .map(
            (
                value
            ) =>
                String(
                    value
                ).toLowerCase()
        );

    return (
        values.includes("terminal") ||
        values.includes("desktop") ||
        values.includes("trading_terminal")
    );
}

function matchesSystemTab(
    record: V2EvidenceRegistryRecord,
    tab: SystemTab
) {
    const metadata = record.metadata ?? {};

    const searchable = [
        record.evidence_hash,
        record.canonical_evidence_id,
        metadata.evidence_category,
        metadata.category,
        metadata.system_category,
        metadata.source_category,
        metadata.object_type,
        metadata.native_object_type,
        metadata.component_type,
        metadata.component_name,
    ]
        .filter(
            (
                value
            ) =>
                value !== null &&
                value !== undefined &&
                value !== ""
        )
        .map(
            (
                value
            ) =>
                String(
                    value
                ).toLowerCase()
        );

    const matchesAny = (
        values: string[]
    ) =>
        values.some(
            (
                value
            ) =>
                searchable.some(
                    (
                        item
                    ) =>
                        item.includes(
                            value
                        )
                )
        );

    switch (tab) {
        case "TERMINAL":
            return (
                isTerminalRecord(
                    record
                )
            );

        case "EXPERT_ADVISORS":
            return matchesAny([
                "expert_advisor",
                "expert advisor",
                "ea",
            ]);

        case "INDICATORS":
            return matchesAny([
                "indicator",
                "technical_indicator",
            ]);

        case "SCRIPTS":
            return matchesAny([
                "script",
                "automation_script",
            ]);

        case "LOGS":
            return matchesAny([
                "log",
                "journal",
                "event_log",
            ]);

        case "CONFIGURATION":
            return matchesAny([
                "configuration",
                "config",
                "settings",
            ]);

        case "CHARTS":
            return matchesAny([
                "chart",
                "chart_state",
                "chart_configuration",
            ]);

        default:
            return false;
    }
}

export default function SystemRecordsPage() {
    const params = useParams<{
        workspaceId: string;
    }>();

    const workspaceId = Number(
        params.workspaceId
    );

    const [
        records,
        setRecords,
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
        activeTab,
        setActiveTab,
    ] = useState<SystemTab>(
        "TERMINAL"
    );

    const [
        loading,
        setLoading,
    ] = useState(true);

    const [
        error,
        setError,
    ] = useState<string | null>(
        null
    );

    async function loadSystemRecords() {
        try {
            setLoading(true);
            setError(null);

            const [
                registryResponse,
                summaryResponse,
            ] = await Promise.all([
                api.getV2EvidenceRegistry(
                    workspaceId
                ),
                api.getV2EvidenceRegistrySummary(
                    workspaceId
                ),
            ]);

            setRecords(
                registryResponse.records
            );

            setSummary(
                summaryResponse
            );
        } catch (err) {
            console.error(err);

            setError(
                err instanceof Error
                    ? err.message
                    : "Unable to load V2 system records."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (!Number.isFinite(workspaceId)) {
            setError(
                "Invalid workspace ID."
            );

            setLoading(false);
            return;
        }

        void loadSystemRecords();
    }, [workspaceId]);

    const filteredRecords = useMemo(
        () =>
            records.filter(
                (
                    record
                ) =>
                    matchesSystemTab(
                        record,
                        activeTab
                    )
            ),
        [
            records,
            activeTab,
        ]
    );

    const activeTabLabel =
        TABS.find(
            (
                tab
            ) =>
                tab.key ===
                activeTab
        )?.label ?? "System Records";

    const systemTypeCounts =
        summary?.evidence_type_counts ?? {};

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
                                System Records
                            </h1>

                            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                                Operational evidence from trading
                                terminals, configurations, software
                                components, logs, and trading-system
                                activity.
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={() =>
                                void loadSystemRecords()
                            }
                            disabled={loading}
                            className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
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
                            System Registry unavailable
                        </div>

                        <div className="mt-1 text-sm text-red-700">
                            {error}
                        </div>
                    </section>
                )}

                <section className="overflow-hidden rounded-2xl border border-slate-300 bg-white shadow-sm">

                    <div className="border-b border-slate-200 px-6 pt-5">
                        <div className="flex flex-wrap gap-2">
                            {TABS.map(
                                (
                                    tab
                                ) => {
                                    const active =
                                        activeTab ===
                                        tab.key;

                                    const count =
                                        records.filter(
                                            (
                                                record
                                            ) =>
                                                matchesSystemTab(
                                                    record,
                                                    tab.key
                                                )
                                        ).length;

                                    return (
                                        <button
                                            key={
                                                tab.key
                                            }
                                            type="button"
                                            onClick={() =>
                                                setActiveTab(
                                                    tab.key
                                                )
                                            }
                                            className={[
                                                "rounded-lg px-4 py-2 text-sm font-semibold transition",
                                                active
                                                    ? "bg-slate-950 text-white"
                                                    : "border border-slate-200 text-slate-600 hover:bg-slate-50",
                                            ].join(
                                                " "
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
                                                    " "
                                                )}
                                            >
                                                {
                                                    count
                                                }
                                            </span>
                                        </button>
                                    );
                                }
                            )}
                        </div>
                    </div>

                    <div className="px-6 py-8">

                        <div className="mb-5">
                            <div className="text-sm font-semibold text-slate-950">
                                {
                                    activeTabLabel
                                }
                            </div>

                            <div className="mt-1 text-xs text-slate-500">
                                {
                                    filteredRecords.length
                                }{" "}
                                records
                            </div>
                        </div>

                        {loading ? (
                            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-16 text-center">
                                <RefreshCw className="mx-auto h-5 w-5 animate-spin text-slate-400" />

                                <div className="mt-3 text-sm font-medium text-slate-600">
                                    Loading system evidence...
                                </div>
                            </div>
                        ) : filteredRecords.length === 0 ? (
                            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-16 text-center">
                                <div className="text-sm font-semibold text-slate-900">
                                    No{" "}
                                    {
                                        activeTabLabel.toLowerCase()
                                    }{" "}
                                    records found
                                </div>

                                <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-slate-500">
                                    This workspace currently has no
                                    registered V2 evidence whose
                                    canonical metadata identifies it as{" "}
                                    {
                                        activeTabLabel.toLowerCase()
                                    }.
                                    Provider connections or system
                                    capability alone do not create a
                                    registry record.
                                </p>
                            </div>
                        ) : (
                            <div className="overflow-x-auto rounded-xl border border-slate-200">
                                <table className="min-w-full text-left">
                                    <thead className="bg-slate-50">
                                        <tr className="border-b border-slate-200">
                                            <th className="px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Evidence
                                            </th>

                                            <th className="px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Provider
                                            </th>

                                            <th className="px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Platform
                                            </th>

                                            <th className="px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Lifecycle
                                            </th>

                                            <th className="px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Registered
                                            </th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {filteredRecords.map(
                                            (
                                                record
                                            ) => (
                                                <tr
                                                    key={
                                                        record.canonical_evidence_id
                                                    }
                                                    className="border-b border-slate-100 last:border-b-0"
                                                >
                                                    <td className="px-4 py-4">
                                                        <div className="font-mono text-xs font-semibold text-slate-900">
                                                            {
                                                                record.canonical_evidence_id
                                                            }
                                                        </div>

                                                        <div className="mt-1 max-w-md break-all text-[10px] text-slate-400">
                                                            {
                                                                record.evidence_hash
                                                            }
                                                        </div>
                                                    </td>

                                                    <td className="px-4 py-4">
                                                        <div className="text-sm font-semibold text-slate-900">
                                                            {
                                                                displayValue(
                                                                    record.provider
                                                                        ?.provider_name
                                                                )
                                                            }
                                                        </div>

                                                        <div className="mt-1 text-xs text-slate-500">
                                                            {
                                                                displayValue(
                                                                    record.provider
                                                                        ?.broker_server
                                                                )
                                                            }
                                                        </div>
                                                    </td>

                                                    <td className="px-4 py-4 text-sm text-slate-700">
                                                        {
                                                            displayValue(
                                                                record.provider
                                                                    ?.provider_platform
                                                            )
                                                        }
                                                    </td>

                                                    <td className="px-4 py-4">
                                                        <span className="rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-medium text-slate-600">
                                                            {
                                                                displayValue(
                                                                    record.lifecycle
                                                                )
                                                            }
                                                        </span>
                                                    </td>

                                                    <td className="px-4 py-4 text-sm text-slate-600">
                                                        {
                                                            formatDate(
                                                                record.registered_at
                                                            )
                                                        }
                                                    </td>
                                                </tr>
                                            )
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        )}

                    </div>
                </section>

                <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">

                    <div className="flex flex-wrap items-start justify-between gap-6">
                        <div>
                            <div className="text-sm font-semibold text-slate-900">
                                Current Registry Evidence
                            </div>

                            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                                These totals are read from the same
                                authoritative V2 registry used by the
                                Evidence Explorer, Trading Records, and
                                Account Records pages.
                            </p>
                        </div>

                        <div className="text-right">
                            <div className="text-xs uppercase tracking-wider text-slate-400">
                                Total V2 Evidence
                            </div>

                            <div className="mt-1 text-2xl font-bold text-slate-950">
                                {
                                    summary?.total_records ??
                                    "—"
                                }
                            </div>
                        </div>
                    </div>

                    <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                        {Object.entries(
                            systemTypeCounts
                        )
                            .sort(
                                (
                                    [, a],
                                    [, b]
                                ) =>
                                    b - a
                            )
                            .map(
                                (
                                    [
                                        type,
                                        count,
                                    ]
                                ) => (
                                    <div
                                        key={
                                            type
                                        }
                                        className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3"
                                    >
                                        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                            {
                                                type
                                            }
                                        </div>

                                        <div className="mt-1 text-lg font-bold text-slate-900">
                                            {
                                                count
                                            }
                                        </div>
                                    </div>
                                )
                            )}
                    </div>
                </section>

            </main>
        </div>
    );
}