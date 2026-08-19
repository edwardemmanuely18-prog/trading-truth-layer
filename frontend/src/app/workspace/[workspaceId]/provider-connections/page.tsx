"use client";

import { useEffect, useState } from "react";
import {
    useParams,
    useRouter,
} from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
    getProviderConnectionsOverview,
    getProviderConnectionActivity,
    getProviderConnections,
    getProviderConnection,
    synchronizeProviderConnection,
    verifyProviderConnection,
    type ProviderConnectionsOverview,
    type ProviderConnectionActivity,
    type ProviderConnectionRecord,
} from "../../../../lib/api";



export default function ProviderConnectionsPage() {

    const router = useRouter();

    const [overview, setOverview] =
        useState<ProviderConnectionsOverview | null>(null);

    const [connections, setConnections] =
        useState<ProviderConnectionRecord[]>([]);

    const [activity, setActivity] =
        useState<ProviderConnectionActivity | null>(null);

    const [lastSuccessfulSync, setLastSuccessfulSync] =
        useState<string | null>(null);

    const [loading, setLoading] =
        useState(true);

    const [refreshingActivity, setRefreshingActivity] =
        useState(false);

    const [synchronizingConnectionId, setSynchronizingConnectionId] =
        useState<string | null>(null);

    const [verifyingConnectionId, setVerifyingConnectionId] =
        useState<string | null>(null);

    const params = useParams<{
        workspaceId: string;
    }>();

    const workspaceId = Number(
        params.workspaceId,
    );

    async function handleSynchronize(
        connection: ProviderConnectionRecord,
    ) {
        setSynchronizingConnectionId(connection.id);

        try {
            await synchronizeProviderConnection(
                workspaceId,
                connection.id,
            );

            const [
                overview,
                connections,
                activityResponse,
            ] = await Promise.all([
                getProviderConnectionsOverview(workspaceId),
                getProviderConnections(workspaceId),
                getProviderConnectionActivity(workspaceId),
            ]);

            setOverview(overview);
            setConnections(connections);
            setActivity(activityResponse);
            await loadLastSuccessfulSync(
                connections,
            );

            const openTradingRecords = window.confirm(
                `Synchronization started for ${connection.connection_name}.\n\nOpen Trading Records to monitor the synchronized evidence?`,
            );

            if (openTradingRecords) {
            router.push(
                `/workspace/${workspaceId}/trading-records`,
            );
            }
        } catch (error) {
            console.error(error);

            alert(
                `Unable to start synchronization for ${connection.connection_name}.`,
            );
        } finally {
            setSynchronizingConnectionId(null);
        }
    }

    async function handleVerify(
        connection: ProviderConnectionRecord,
    ) {
        try {
            setVerifyingConnectionId(connection.id);

            const result = await verifyProviderConnection(
                workspaceId,
                connection.id,
            );

            const updatedConnections =
                await getProviderConnections(workspaceId);

            setConnections(updatedConnections);

            if (result.verified) {
                alert(
                    `Verification successful for ${connection.connection_name}.`,
                );
            } else {
                alert(
                    `Verification failed for ${connection.connection_name}.`,
                );
            }
        } catch (error) {
            console.error(error);

            alert(
                `Unable to verify ${connection.connection_name}.`,
            );
        } finally {
            setVerifyingConnectionId(null);
        }
    }

    async function loadLastSuccessfulSync(
        providerConnections: ProviderConnectionRecord[],
    ) {
        if (providerConnections.length === 0) {
            setLastSuccessfulSync(null);
            return;
        }

        try {
            const details = await Promise.all(
                providerConnections.map((connection) =>
                    getProviderConnection(
                        workspaceId,
                        connection.id,
                    ),
                ),
            );

            const successfulSyncs = details
                .filter(
                    (detail) =>
                        detail.statistics.successful_synchronizations > 0 &&
                        detail.statistics.last_synchronization,
                )
                .map(
                    (detail) =>
                        detail.statistics.last_synchronization as string,
                );

            if (successfulSyncs.length === 0) {
                setLastSuccessfulSync(null);
                return;
            }

            const latest = successfulSyncs.reduce(
                (latestValue, currentValue) =>
                    new Date(currentValue) > new Date(latestValue)
                        ? currentValue
                        : latestValue,
            );

            setLastSuccessfulSync(latest);
        } catch (error) {
            console.error(
                "Unable to load last successful synchronization:",
                error,
            );

            setLastSuccessfulSync(null);
        }
    }

    useEffect(() => {

        let mounted = true;

        async function load() {

            try {

                const [
                    updatedOverview,
                    updatedConnections,
                    updatedActivity,
                ] = await Promise.all([
                    getProviderConnectionsOverview(workspaceId),
                    getProviderConnections(workspaceId),
                    getProviderConnectionActivity(workspaceId),
                ]);

                if (mounted) {

                    setOverview(updatedOverview);
                    setConnections(updatedConnections);
                    setActivity(updatedActivity);

                    await loadLastSuccessfulSync(
                        updatedConnections,
                    );

                }

            } catch (error) {

                console.error(error);

            } finally {

                if (mounted) {

                    setLoading(false);

                }

            }

        }

        load();

        return () => {

            mounted = false;

        };

    }, [workspaceId]);

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50">
                <Navbar />

                <div className="mx-auto max-w-7xl px-6 py-10">
                    <div className="rounded-2xl border bg-white p-16 text-center">
                        <div className="text-lg font-semibold text-slate-700">
                            Loading Provider Connections...
                        </div>

                        <div className="mt-2 text-sm text-slate-500">
                            Loading the provider connection registry and runtime status.
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (

        <div className="min-h-screen bg-slate-50">

            <Navbar />

            <div className="mx-auto max-w-7xl px-6 py-10">

                {/* ====================================================== */}
                {/* Hero */}
                {/* ====================================================== */}

                <div className="mb-10">

                    <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
                        INSTITUTIONAL PROVIDER CONNECTION INFRASTRUCTURE
                    </div>

                    <h1 className="mt-2 text-5xl font-bold">
                        Provider Connections
                    </h1>

                    <p className="mt-4 max-w-5xl text-slate-600 leading-7">

                        Institutional infrastructure responsible for
                        establishing, authenticating, managing and
                        monitoring trusted connections between Trading
                        Truth Layer and external evidence providers
                        operating across desktop trading platforms,
                        gateway infrastructures and institutional
                        financial networks.

                    </p>

                </div>

                {/* ====================================================== */}
                {/* Executive Summary */}
                {/* ====================================================== */}

                <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-6 mb-8">

                    <MetricCard
                        title="Supported Providers"
                        value={
                            overview?.summary.supported_providers ?? 0
                        }
                    />

                    <MetricCard
                        title="Configured Connections"
                        value={
                            overview?.summary.configured_connections ?? 0
                        }
                    />

                    <MetricCard
                        title="Verified Connections"
                        value={
                            connections.filter(
                                (connection) => connection.verified,
                            ).length
                        }
                    />

                    <MetricCard
                        title="Healthy Connections"
                        value={
                            overview?.summary.healthy_connections ?? 0
                        }
                    />

                    <MetricCard
                        title="Synchronizing"
                        value={
                            overview?.summary.synchronizing ?? 0
                        }
                    />

                    <MetricCard
                        title="Evidence Packages"
                        value={
                            overview?.summary.evidence_packages ?? 0
                        }
                    />

                </div>

                {/* ====================================================== */}
                {/* Connection Engines */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">
                        Connection Engines
                    </h2>

                    <p className="mt-2 text-slate-500">

                        Evidence providers are organized by their canonical
                        acquisition engine. Select an engine to configure
                        provider connections, authenticate external systems
                        and begin institutional evidence acquisition.

                    </p>

                    <div className="mt-8 grid gap-6 lg:grid-cols-3">

                        <ConnectionEngineCard
                            title="Desktop Trading Engine"
                            providers={
                                String(
                                    overview?.engines.desktop.supported_providers ?? 0,
                                )
                            }
                            connections={
                                String(
                                    overview?.engines.desktop.configured_connections ?? 0,
                                )
                            }
                            healthy={
                                String(
                                    overview?.engines.desktop.healthy ?? false,
                                )
                            }
                            status={
                                overview?.engines.desktop?.healthy
                                    ? "READY"
                                    : "CLEAR"
                            }
                            href={`/workspace/${workspaceId}/provider-connections/desktop`}
                        />

                        <ConnectionEngineCard
                            title="Gateway Engine"
                            providers={
                                String(
                                    overview?.engines.gateway.supported_providers ?? 0,
                                )
                            }
                            connections={
                                String(
                                    overview?.engines.gateway.configured_connections ?? 0,
                                )
                            }
                            healthy={
                                String(
                                    overview?.engines.gateway.healthy ?? false,
                                )
                            }
                            status={
                                overview?.engines.gateway?.healthy
                                    ? "READY"
                                    : "CLEAR"
                            }
                            href={`/workspace/${workspaceId}/provider-connections/gateway`}
                        />

                        <ConnectionEngineCard
                            title="Financial Engine"
                            providers={
                                String(
                                    overview?.engines.financial.supported_providers ?? 0,
                                )
                            }
                            connections={
                                String(
                                    overview?.engines.financial.configured_connections ?? 0,
                                )
                            }
                            healthy={
                                String(
                                    overview?.engines.financial.healthy ?? false,
                                )
                            }
                            status={
                                overview?.engines.financial?.healthy
                                    ? "READY"
                                    : "CLEAR"
                            }
                            href={`/workspace/${workspaceId}/provider-connections/financial`}
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Active Provider Connections */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">
                                Active Provider Connections
                            </h2>

                            <p className="mt-2 text-slate-500">

                                Operational registry of authenticated provider
                                connections currently managed by the Evidence
                                Acquisition Runtime.

                            </p>

                        </div>

                        <button
                            onClick={() =>
                                router.push(
                                    `/workspace/${workspaceId}/provider-connections/desktop/new`,
                                )
                            }
                            className="rounded-lg bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
                        >
                            New Connection
                        </button>

                    </div>

                    <div className="mt-8 overflow-x-auto rounded-xl border border-slate-200">
                        <table className="min-w-[1500px] w-full border-collapse bg-white">
                            <thead className="bg-slate-50">
                                <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-[0.08em] text-slate-500">

                                    <th className="w-[260px] px-4 py-4 font-semibold whitespace-nowrap">
                                        Connection
                                    </th>

                                    <th className="w-[150px] px-4 py-4 font-semibold whitespace-nowrap">
                                        Provider
                                    </th>

                                    <th className="w-[210px] px-4 py-4 font-semibold whitespace-nowrap">
                                        Engine
                                    </th>

                                    <th className="w-[120px] px-4 py-4 font-semibold whitespace-nowrap">
                                        Environment
                                    </th>

                                    <th className="w-[110px] px-4 py-4 font-semibold whitespace-nowrap">
                                        Health
                                    </th>

                                    <th className="w-[145px] px-4 py-4 font-semibold whitespace-nowrap">
                                        Verification
                                    </th>

                                    <th className="w-[170px] px-4 py-4 font-semibold whitespace-nowrap">
                                        Connection Status
                                    </th>

                                    <th className="w-[160px] px-4 py-4 font-semibold whitespace-nowrap">
                                        Synchronization
                                    </th>

                                    <th className="w-[215px] px-4 py-4 font-semibold whitespace-nowrap">
                                        Actions
                                    </th>

                                </tr>
                            </thead>

                            <tbody>

                                {

                                    connections.length === 0

                                    ? (

                                        <EmptyConnectionRow
                                            onCreate={() =>
                                                router.push(
                                                    `/workspace/${workspaceId}/provider-connections/desktop/new`,
                                                )
                                            }
                                        />

                                    )

                                    : (

                                        connections.map((connection) => (
                                            <tr
                                                key={connection.id}
                                                className="border-b last:border-b-0 hover:bg-slate-50"
                                            >
                                                {/* Connection */}
                                                <td className="px-4 py-5 align-middle">
                                                    <div
                                                        className="truncate font-medium text-slate-900"
                                                        title={connection.connection_name}
                                                    >
                                                        {connection.connection_name}
                                                    </div>

                                                    <div className="mt-1 text-xs text-slate-400">
                                                        {connection.id}
                                                    </div>
                                                </td>

                                                {/* Provider */}
                                                <td className="px-4 py-5 align-middle">
                                                    <div className="font-medium text-slate-900">
                                                        {connection.provider}
                                                    </div>
                                                </td>

                                                {/* Engine */}
                                                <td className="px-4 py-5 align-middle">
                                                    <div
                                                        className="truncate text-sm text-slate-700"
                                                        title={connection.engine}
                                                    >
                                                        {connection.engine}
                                                    </div>
                                                </td>

                                                {/* Environment */}
                                                <td className="px-4 py-5 align-middle">
                                                    <span className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold capitalize text-slate-700">
                                                        {connection.environment}
                                                    </span>
                                                </td>

                                                {/* Health */}
                                                <td className="px-4 py-5 align-middle">
                                                    <span
                                                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                                                            connection.health === "healthy"
                                                                ? "bg-green-100 text-green-700"
                                                                : connection.health === "warning"
                                                                ? "bg-yellow-100 text-yellow-700"
                                                                : "bg-slate-100 text-slate-700"
                                                        }`}
                                                    >
                                                        {connection.health}
                                                    </span>
                                                </td>

                                                {/* Verification */}
                                                <td className="px-4 py-5 align-middle">
                                                    <span
                                                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                                                            connection.verified
                                                                ? "bg-green-100 text-green-700"
                                                                : "bg-yellow-100 text-yellow-700"
                                                        }`}
                                                    >
                                                        {connection.verified
                                                            ? "Verified"
                                                            : "Pending"}
                                                    </span>
                                                </td>

                                                {/* Connection Status */}
                                                <td className="px-4 py-5 align-middle">
                                                    <span
                                                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                                                            connection.connected
                                                                ? "bg-green-100 text-green-700"
                                                                : "bg-slate-100 text-slate-700"
                                                        }`}
                                                    >
                                                        {connection.connected
                                                            ? "Connected"
                                                            : "Disconnected"}
                                                    </span>
                                                </td>

                                                {/* Synchronization */}
                                                <td className="px-4 py-5 align-middle">
                                                    <span
                                                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                                                            connection.status === "synchronizing"
                                                                ? "bg-blue-100 text-blue-700"
                                                                : connection.status === "failed"
                                                                ? "bg-red-100 text-red-700"
                                                                : connection.connected
                                                                ? "bg-slate-100 text-slate-700"
                                                                : "bg-slate-100 text-slate-700"
                                                        }`}
                                                    >
                                                        {connection.status === "synchronizing"
                                                            ? "Synchronizing..."
                                                            : connection.status === "failed"
                                                            ? "Failed"
                                                            : connection.connected
                                                            ? "Ready"
                                                            : "Disconnected"}
                                                    </span>
                                                </td>

                                                {/* Actions */}
                                                <td className="py-5 align-middle">
                                                    <div className="flex items-center gap-2 whitespace-nowrap">
                                                        <button
                                                            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-semibold whitespace-nowrap text-slate-700 hover:bg-slate-100"
                                                            onClick={() =>
                                                                router.push(
                                                                    `/workspace/${workspaceId}/provider-connections/${encodeURIComponent(
                                                                        connection.id,
                                                                    )}`,
                                                                )
                                                            }
                                                        >
                                                            View
                                                        </button>

                                                        <button
                                                            className="rounded-lg border border-blue-600 px-3 py-2 text-xs font-semibold text-blue-700 hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
                                                            onClick={() =>
                                                                handleVerify(connection)
                                                            }
                                                            disabled={
                                                                verifyingConnectionId ===
                                                                connection.id
                                                            }
                                                        >
                                                            {verifyingConnectionId ===
                                                            connection.id
                                                                ? "Verifying..."
                                                                : connection.verified
                                                                ? "Re-verify"
                                                                : "Verify"}
                                                        </button>

                                                        <button
                                                            className="rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                                                            onClick={() =>
                                                                handleSynchronize(
                                                                    connection,
                                                                )
                                                            }
                                                            disabled={
                                                                synchronizingConnectionId ===
                                                                    connection.id ||
                                                                connection.status ===
                                                                    "synchronizing"
                                                            }
                                                        >
                                                            {synchronizingConnectionId ===
                                                                connection.id ||
                                                            connection.status ===
                                                                "synchronizing"
                                                                ? "Synchronizing..."
                                                                : "Synchronize"}
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))

                                    )

                                }

                            </tbody>

                        </table>

                    </div>

                </div>

                                {/* ====================================================== */}
                {/* Connection Health */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">
                        Connection Health & Verification
                    </h2>

                    <p className="mt-2 text-slate-500">

                        Institutional operational overview of provider
                        authentication, verification, synchronization
                        readiness and runtime health across all connected
                        acquisition engines.

                    </p>

                    <div className="mt-8 grid gap-5 lg:grid-cols-3">

                        <HealthCard
                            title="Healthy Connections"
                            value={String(
                                overview?.summary.healthy_connections ?? 0,
                            )}
                            status={
                                (overview?.summary.healthy_connections ?? 0) > 0
                                    ? "READY"
                                    : "CLEAR"
                            }
                        />

                        <HealthCard
                            title="Pending Verification"
                            value={String(
                                connections.filter(
                                    (connection) => !connection.verified,
                                ).length,
                            )}
                            status={
                                connections.some(
                                    (connection) => !connection.verified,
                                )
                                    ? "WAITING"
                                    : "CLEAR"
                            }
                        />

                        <HealthCard
                            title="Failed Connections"
                            value={String(
                                connections.filter(
                                    (connection) => connection.status === "failed",
                                ).length,
                            )}
                            status={
                                connections.some(
                                    (connection) => connection.status === "failed",
                                )
                                    ? "ERROR"
                                    : "CLEAR"
                            }
                        />

                        <HealthCard
                            title="Synchronization Errors"
                            value="Not reported"
                            status="N/A"
                        />

                        <HealthCard
                            title="Runtime Warnings"
                            value={String(
                                connections.filter(
                                    (connection) => connection.health === "warning",
                                ).length,
                            )}
                            status={
                                connections.some(
                                    (connection) => connection.health === "warning",
                                )
                                    ? "WAITING"
                                    : "CLEAR"
                            }
                        />

                        <HealthCard
                            title="Last Successful Sync"
                            value={
                                lastSuccessfulSync
                                    ? new Date(
                                        lastSuccessfulSync,
                                    ).toLocaleString()
                                    : "Not reported"
                            }
                            status={
                                lastSuccessfulSync
                                    ? "READY"
                                    : "N/A"
                            }
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Recent Provider Activity */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">
                                Recent Provider Activity
                            </h2>

                            <p className="mt-2 text-slate-500">

                                Institutional timeline of provider
                                authentication, connection lifecycle,
                                synchronization operations and evidence
                                acquisition activities across every
                                acquisition engine.

                            </p>

                        </div>

                        <button
                            onClick={async () => {
                                setRefreshingActivity(true);

                                try {
                                    const updatedActivity =
                                        await getProviderConnectionActivity(
                                            workspaceId,
                                        );

                                    setActivity(updatedActivity);
                                } catch (error) {
                                    console.error(error);

                                    alert(
                                        "Unable to refresh provider activity.",
                                    );
                                } finally {
                                    setRefreshingActivity(false);
                                }
                            }}
                            className="rounded-lg bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
                        >
                            {refreshingActivity
                                ? "Refreshing..."
                                : "Refresh Activity"}
                        </button>

                    </div>

                    <div className="mt-8">

                        <ActivitySummary activity={activity} />

                    </div>

                </div>



            </div>

        </div>

    );

}

function MetricCard({
    title,
    value,
}: {
    title: string;
    value: string | number;
}) {

    return (

        <div className="rounded-2xl border bg-white p-6 shadow-sm">

            <div className="text-sm text-slate-500">

                {title}

            </div>

            <div className="mt-2 text-4xl font-bold">

                {value}

            </div>

        </div>

    );

}

function ConnectionEngineCard({
    title,
    providers,
    connections,
    healthy,
    status,
    href,
}: {
    title: string;
    providers: string;
    connections: string;
    healthy: string;
    status: string;
    href: string;
}) {

    const router = useRouter();

    const handleOpen = () => {

        router.push(href);

    };

    return (

        <div className="rounded-2xl border bg-slate-50 p-6">

            <div className="flex items-center justify-between">

                <div>

                    <div className="text-xl font-semibold">

                        {title}

                    </div>

                    <div className="mt-1 text-sm text-slate-500">

                        Canonical Evidence Acquisition Engine

                    </div>

                </div>

                <div className="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">

                    {status}

                </div>

            </div>

            <div className="mt-8 space-y-3 text-sm">

                <EngineMetric
                    label="Supported Providers"
                    value={providers}
                />

                <EngineMetric
                    label="Configured Connections"
                    value={connections}
                />

                <EngineMetric
                    label="Healthy Connections"
                    value={healthy}
                />

            </div>

            <button
                onClick={handleOpen}
                className="mt-8 w-full rounded-lg bg-slate-900 px-4 py-3 text-sm font-semibold text-white hover:bg-slate-800"
            >
                Open Engine
            </button>

        </div>

    );

}

function EngineMetric({
    label,
    value,
}: {
    label: string;
    value: string;
}) {

    return (

        <div className="flex items-center justify-between border-b pb-2">

            <span className="text-slate-500">

                {label}

            </span>

            <span className="font-semibold">

                {value}

            </span>

        </div>

    );

}

function EmptyConnectionRow({
    onCreate,
}: {
    onCreate: () => void;
}) {
    return (
        <tr>
            <td
                colSpan={9}
                className="py-16 text-center"
            >
                <div className="text-lg font-semibold text-slate-700">
                    No Provider Connections
                </div>

                <div className="mt-2 text-sm text-slate-500">
                    Create your first authenticated provider connection
                    to begin institutional evidence acquisition.
                </div>

                <button
                    onClick={onCreate}
                    className="mt-6 rounded-lg bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
                >
                    Create First Connection
                </button>
            </td>
        </tr>
    );
}

function HealthCard({
    title,
    value,
    status,
}: {
    title: string;
    value: string;
    status: string;
}) {

    const badgeClass =
        status === "READY"
            ? "bg-green-100 text-green-700"
            : status === "WAITING"
            ? "bg-yellow-100 text-yellow-700"
            : status === "CLEAR"
            ? "bg-blue-100 text-blue-700"
            : "bg-slate-100 text-slate-700";

    return (

        <div className="rounded-2xl border bg-slate-50 p-6">

            <div className="flex items-center justify-between">

                <div className="text-lg font-semibold">

                    {title}

                </div>

                <div
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${badgeClass}`}
                >
                    {status}
                </div>

            </div>

            <div className="mt-6 text-4xl font-bold">

                {value}

            </div>

        </div>

    );

}

function ActivitySummary({
    activity,
}: {
    activity: ProviderConnectionActivity | null;
}) {

    if (!activity) {
        return (
            <div className="rounded-xl border bg-slate-50 p-6">

                <div className="text-lg font-semibold text-slate-700">
                    No Provider Activity Reported
                </div>

                <div className="mt-2 text-sm leading-6 text-slate-500">
                    Provider runtime activity statistics are not currently
                    available.
                </div>

            </div>
        );
    }

    return (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">

            <ActivityMetric
                label="Total Connections"
                value={activity.total}
            />

            <ActivityMetric
                label="Connected"
                value={activity.connected}
            />

            <ActivityMetric
                label="Disconnected"
                value={activity.disconnected}
            />

            <ActivityMetric
                label="Failed"
                value={activity.failed}
            />

            <ActivityMetric
                label="Synchronizing"
                value={activity.synchronizing}
            />

        </div>
    );
}

function ActivityMetric({
    label,
    value,
}: {
    label: string;
    value: number;
}) {

    return (
        <div className="rounded-xl border bg-slate-50 p-5">

            <div className="text-sm text-slate-500">
                {label}
            </div>

            <div className="mt-3 text-3xl font-bold">
                {value}
            </div>

        </div>
    );
}