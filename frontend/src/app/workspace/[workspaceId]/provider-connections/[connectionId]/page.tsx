"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import Navbar from "../../../../../components/Navbar";

import {
    getProviderConnection,
    type ProviderConnectionDetail,
} from "../../../../../lib/api";

function formatDate(value: string | null) {
    if (!value) {
        return "Not available";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}

function formatLabel(value: string) {
    if (!value) {
        return "—";
    }

    return value
        .replace(/_/g, " ")
        .replace(/\b\w/g, (character) => character.toUpperCase());
}

function StatusBadge({
    value,
    tone,
}: {
    value: string;
    tone?: "success" | "warning" | "error" | "neutral";
}) {
    const resolvedTone =
        tone ??
        (value === "connected" || value === "healthy"
            ? "success"
            : value === "warning" || value === "synchronizing"
              ? "warning"
              : value === "failed" || value === "error"
                ? "error"
                : "neutral");

    const classes = {
        success:
            "border-emerald-200 bg-emerald-50 text-emerald-700",
        warning:
            "border-amber-200 bg-amber-50 text-amber-700",
        error:
            "border-red-200 bg-red-50 text-red-700",
        neutral:
            "border-slate-200 bg-slate-50 text-slate-700",
    };

    return (
        <span
            className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${classes[resolvedTone]}`}
        >
            {formatLabel(value)}
        </span>
    );
}

function MetricCard({
    label,
    value,
}: {
    label: string;
    value: string | number;
}) {
    return (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
                {label}
            </div>

            <div className="mt-2 text-2xl font-semibold text-slate-900">
                {value}
            </div>
        </div>
    );
}

function DetailRow({
    label,
    value,
}: {
    label: string;
    value: React.ReactNode;
}) {
    return (
        <div className="flex items-center justify-between gap-6 border-b border-slate-100 py-4 last:border-b-0">
            <div className="text-sm text-slate-500">
                {label}
            </div>

            <div className="text-right text-sm font-medium text-slate-900">
                {value}
            </div>
        </div>
    );
}

export default function ProviderConnectionDetailPage() {
    const params = useParams();
    const router = useRouter();

    const workspaceId = Number(params.workspaceId);
    const connectionId = decodeURIComponent(
        String(params.connectionId),
    );

    const [connection, setConnection] =
        useState<ProviderConnectionDetail | null>(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [refreshing, setRefreshing] = useState(false);

    async function loadConnection(
        showInitialLoader = false,
    ) {
        try {
            if (showInitialLoader) {
                setLoading(true);
            } else {
                setRefreshing(true);
            }

            setError(null);

            const result = await getProviderConnection(
                workspaceId,
                connectionId,
            );

            setConnection(result);
        } catch (err) {
            console.error(err);

            setError(
                err instanceof Error
                    ? err.message
                    : "Failed to load provider connection.",
            );
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }

    useEffect(() => {
        if (
            !Number.isFinite(workspaceId) ||
            !connectionId
        ) {
            setError("Invalid provider connection route.");
            setLoading(false);
            return;
        }

        void loadConnection(true);
    }, [workspaceId, connectionId]);

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50">
                <Navbar />

                <main className="mx-auto max-w-7xl px-6 py-10">
                    <div className="rounded-3xl border border-slate-200 bg-white p-10 shadow-sm">
                        <div className="text-sm text-slate-500">
                            Loading provider connection...
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    if (error || !connection) {
        return (
            <div className="min-h-screen bg-slate-50">
                <Navbar />

                <main className="mx-auto max-w-7xl px-6 py-10">
                    <div className="rounded-3xl border border-red-200 bg-white p-10 shadow-sm">
                        <h1 className="text-xl font-semibold text-slate-900">
                            Provider Connection Unavailable
                        </h1>

                        <p className="mt-3 text-sm text-red-600">
                            {error ??
                                "The provider connection could not be loaded."}
                        </p>

                        <button
                            type="button"
                            onClick={() => router.back()}
                            className="mt-6 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                        >
                            Back
                        </button>
                    </div>
                </main>
            </div>
        );
    }

    const statistics = connection.statistics;

    return (
        <div className="min-h-screen bg-slate-50">
            <Navbar />

            <main className="mx-auto max-w-7xl px-6 py-10">
                {/* Header */}
                <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                        <button
                            type="button"
                            onClick={() => router.back()}
                            className="mb-4 text-sm font-medium text-slate-500 hover:text-slate-900"
                        >
                            ← Back to Provider Connections
                        </button>

                        <div className="flex flex-wrap items-center gap-3">
                            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                                {connection.connection_name}
                            </h1>

                            <StatusBadge
                                value={connection.status}
                            />

                            <StatusBadge
                                value={connection.health}
                            />
                        </div>

                        <p className="mt-2 text-sm text-slate-500">
                            Provider Connection
                        </p>
                    </div>

                    <button
                        type="button"
                        disabled={refreshing}
                        onClick={() =>
                            void loadConnection(false)
                        }
                        className="rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        {refreshing
                            ? "Refreshing..."
                            : "Refresh"}
                    </button>
                </div>

                {/* Runtime state */}
                <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                    <MetricCard
                        label="Provider"
                        value={connection.provider}
                    />

                    <MetricCard
                        label="Engine"
                        value={formatLabel(
                            connection.engine,
                        )}
                    />

                    <MetricCard
                        label="Environment"
                        value={formatLabel(
                            connection.environment,
                        )}
                    />

                    <MetricCard
                        label="Verification"
                        value={
                            connection.verified
                                ? "Verified"
                                : "Not Verified"
                        }
                    />
                </section>

                {/* Identity + runtime */}
                <section className="mt-6 grid gap-6 lg:grid-cols-2">
                    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                        <h2 className="text-lg font-semibold text-slate-900">
                            Connection Identity
                        </h2>

                        <div className="mt-4">
                            <DetailRow
                                label="Connection ID"
                                value={
                                    <span className="break-all font-mono text-xs">
                                        {connection.id}
                                    </span>
                                }
                            />

                            <DetailRow
                                label="Workspace"
                                value={connection.workspace_id}
                            />

                            <DetailRow
                                label="Provider"
                                value={connection.provider}
                            />

                            <DetailRow
                                label="Engine"
                                value={formatLabel(
                                    connection.engine,
                                )}
                            />

                            <DetailRow
                                label="Environment"
                                value={formatLabel(
                                    connection.environment,
                                )}
                            />
                        </div>
                    </div>

                    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                        <h2 className="text-lg font-semibold text-slate-900">
                            Runtime State
                        </h2>

                        <div className="mt-4">
                            <DetailRow
                                label="Connection Status"
                                value={
                                    <StatusBadge
                                        value={
                                            connection.status
                                        }
                                    />
                                }
                            />

                            <DetailRow
                                label="Health"
                                value={
                                    <StatusBadge
                                        value={
                                            connection.health
                                        }
                                    />
                                }
                            />

                            <DetailRow
                                label="Connected"
                                value={
                                    <StatusBadge
                                        value={
                                            connection.connected
                                                ? "connected"
                                                : "disconnected"
                                        }
                                    />
                                }
                            />

                            <DetailRow
                                label="Verified"
                                value={
                                    <StatusBadge
                                        value={
                                            connection.verified
                                                ? "verified"
                                                : "not verified"
                                        }
                                    />
                                }
                            />
                        </div>
                    </div>
                </section>

                {/* Synchronization statistics */}
                <section className="mt-6">
                    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                            <div>
                                <h2 className="text-lg font-semibold text-slate-900">
                                    Synchronization Statistics
                                </h2>

                                <p className="mt-1 text-sm text-slate-500">
                                    Runtime statistics reported by the
                                    Provider Connection.
                                </p>
                            </div>
                        </div>

                        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                            <MetricCard
                                label="Synchronizations"
                                value={
                                    statistics.synchronization_count
                                }
                            />

                            <MetricCard
                                label="Successful"
                                value={
                                    statistics.successful_synchronizations
                                }
                            />

                            <MetricCard
                                label="Failed"
                                value={
                                    statistics.failed_synchronizations
                                }
                            />

                            <MetricCard
                                label="Evidence Packages"
                                value={
                                    statistics.evidence_packages
                                }
                            />
                        </div>

                        <div className="mt-6 border-t border-slate-100 pt-2">
                            <DetailRow
                                label="Last Synchronization"
                                value={formatDate(
                                    statistics.last_synchronization,
                                )}
                            />
                        </div>
                    </div>
                </section>

                {/* Lifecycle */}
                <section className="mt-6">
                    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                        <h2 className="text-lg font-semibold text-slate-900">
                            Lifecycle
                        </h2>

                        <div className="mt-4">
                            <DetailRow
                                label="Created"
                                value={formatDate(
                                    connection.created_at,
                                )}
                            />

                            <DetailRow
                                label="Last Updated"
                                value={formatDate(
                                    connection.updated_at,
                                )}
                            />
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}