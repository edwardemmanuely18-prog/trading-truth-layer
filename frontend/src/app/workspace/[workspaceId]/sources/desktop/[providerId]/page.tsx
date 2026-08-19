"use client";

import {
    useEffect,
    useState,
} from "react";

import {
    useParams,
    useRouter,
} from "next/navigation";

import Navbar from "../../../../../../components/Navbar";

import {
    getProviderConnections,
    getProviderConnection,
    synchronizeProviderConnection,
    verifyProviderConnection,
    type ProviderConnectionRecord,
    type ProviderConnectionDetail,
} from "../../../../../../lib/api";

export default function DesktopProviderPage() {

    const params = useParams<{
        workspaceId: string;
        providerId: string;
    }>();

    const router = useRouter();

    const workspaceId = Number(
        params.workspaceId,
    );

    const providerId = String(
        params.providerId,
    );

    const [connections, setConnections] =
        useState<ProviderConnectionRecord[]>([]);

    const [selectedConnection, setSelectedConnection] =
        useState<ProviderConnectionDetail | null>(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState<string | null>(null);

    const [synchronizingConnectionId, setSynchronizingConnectionId] =
        useState<string | null>(null);

    const [verifyingConnectionId, setVerifyingConnectionId] =
        useState<string | null>(null);

    useEffect(() => {
        let mounted = true;

        async function loadProvider() {
            try {
                setLoading(true);
                setError(null);

                const records =
                    await getProviderConnections(
                        workspaceId,
                    );

                const providerConnections =
                    records.filter(
                        (connection) =>
                            connection.provider.toLowerCase()
                                === providerId.toLowerCase(),
                    );

                if (!mounted) {
                    return;
                }

                setConnections(
                    providerConnections,
                );

                if (
                    providerConnections.length > 0
                ) {
                    const detail =
                        await getProviderConnection(
                            workspaceId,
                            providerConnections[0].id,
                        );

                    if (mounted) {
                        setSelectedConnection(
                            detail,
                        );
                    }
                } else {
                    setSelectedConnection(null);
                }
            } catch (err) {
                if (mounted) {
                    setError(
                        err instanceof Error
                            ? err.message
                            : "Unable to load provider connections.",
                    );
                }
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        }

        if (
            !Number.isNaN(workspaceId) &&
            providerId
        ) {
            loadProvider();
        }

        return () => {
            mounted = false;
        };
    }, [
        workspaceId,
        providerId,
    ]);

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50">
                <Navbar />

                <div className="mx-auto max-w-7xl px-6 py-10">
                    Loading Desktop Provider...
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-slate-50">
                <Navbar />

                <div className="mx-auto max-w-7xl px-6 py-10">
                    <div className="rounded-2xl border bg-white p-8">
                        <h1 className="text-2xl font-semibold">
                            Unable to load provider
                        </h1>

                        <p className="mt-3 text-slate-600">
                            {error}
                        </p>

                        <button
                            type="button"
                            onClick={() =>
                                router.back()
                            }
                            className="mt-6 rounded-lg bg-slate-900 px-4 py-2 text-white hover:bg-slate-800"
                        >
                            Go Back
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    async function handleSynchronize(
        connection: ProviderConnectionRecord,
    ) {
        setSynchronizingConnectionId(
            connection.id,
        );

        try {
            await synchronizeProviderConnection(
                workspaceId,
                connection.id,
            );

            const updatedConnections =
                await getProviderConnections(
                    workspaceId,
                );

            const providerConnections =
                updatedConnections.filter(
                    (item) =>
                        item.provider.toLowerCase()
                        === providerId.toLowerCase(),
                );

            setConnections(
                providerConnections,
            );

            if (
                providerConnections.length > 0
            ) {
                const detail =
                    await getProviderConnection(
                        workspaceId,
                        providerConnections[0].id,
                    );

                setSelectedConnection(
                    detail,
                );
            }

            alert(
                `Synchronization started for ${connection.connection_name}.`,
            );
        } catch (err) {
            console.error(err);

            alert(
                `Unable to synchronize ${connection.connection_name}.`,
            );
        } finally {
            setSynchronizingConnectionId(
                null,
            );
        }
    }

    async function handleVerify(
        connection: ProviderConnectionRecord,
    ) {
        setVerifyingConnectionId(
            connection.id,
        );

        try {
            const result =
                await verifyProviderConnection(
                    workspaceId,
                    connection.id,
                );

            const updatedConnections =
                await getProviderConnections(
                    workspaceId,
                );

            const providerConnections =
                updatedConnections.filter(
                    (item) =>
                        item.provider.toLowerCase()
                        === providerId.toLowerCase(),
                );

            setConnections(
                providerConnections,
            );

            if (
                providerConnections.length > 0
            ) {
                const detail =
                    await getProviderConnection(
                        workspaceId,
                        providerConnections[0].id,
                    );

                setSelectedConnection(
                    detail,
                );
            }

            alert(
                result.verified
                    ? `Verification successful for ${connection.connection_name}.`
                    : `Verification failed for ${connection.connection_name}.`,
            );
        } catch (err) {
            console.error(err);

            alert(
                `Unable to verify ${connection.connection_name}.`,
            );
        } finally {
            setVerifyingConnectionId(
                null,
            );
        }
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

                        DESKTOP TRADING PROVIDER

                    </div>

                    <h1 className="mt-2 text-5xl font-bold">

                        {providerId.toUpperCase()}

                    </h1>

                    <p className="mt-4 max-w-5xl leading-7 text-slate-600">

                        Canonical provider interface responsible for
                        managing desktop trading infrastructure,
                        provider connections, synchronization,
                        diagnostics and institutional evidence
                        acquisition.

                    </p>

                </div>

                {/* ====================================================== */}
                {/* Provider Identity */}
                {/* ====================================================== */}

                <div className="grid gap-4 md:grid-cols-4 mb-8">

                    <IdentityCard
                        title="Workspace"
                        value={String(workspaceId)}
                    />

                    <IdentityCard
                        title="Provider"
                        value={providerId}
                    />

                    <IdentityCard
                        title="Engine"
                        value="Desktop Trading"
                    />

                    <IdentityCard
                        title="Runtime"
                        value={
                            selectedConnection
                                ? selectedConnection.health.toUpperCase()
                                : connections.length > 0
                                    ? "CONNECTED"
                                    : "NO CONNECTION"
                        }
                    />

                </div>

                {/* ====================================================== */}
                {/* Operational Summary */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">

                        Operational Summary

                    </h2>

                    <p className="mt-2 text-slate-500">

                        High-level operational metrics for this desktop provider.

                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-6">

                        <SummaryCard
                            title="Connections"
                            value={String(connections.length)}
                        />

                        <SummaryCard
                            title="Connected"
                            value={
                                String(
                                    connections.filter(
                                        (connection) =>
                                            connection.connected,
                                    ).length,
                                )
                            }
                        />

                        <SummaryCard
                            title="Verified"
                            value={
                                String(
                                    connections.filter(
                                        (connection) =>
                                            connection.verified,
                                    ).length,
                                )
                            }
                        />

                        <SummaryCard
                            title="Synchronizing"
                            value={
                                String(
                                    connections.filter(
                                        (connection) =>
                                            connection.status
                                                .toLowerCase()
                                                .includes("synchron"),
                                    ).length,
                                )
                            }
                        />

                        <SummaryCard
                            title="Evidence"
                            value={
                                selectedConnection
                                    ? String(
                                        selectedConnection.statistics
                                            .evidence_packages,
                                    )
                                    : "0"
                            }
                        />

                        <SummaryCard
                            title="Health"
                            value={
                                selectedConnection
                                    ? selectedConnection.health.toUpperCase()
                                    : connections.length > 0
                                        ? "CONNECTED"
                                        : "NO CONNECTION"
                            }
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Connections */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Connections

                            </h2>

                            <p className="mt-2 text-slate-500">

                                Desktop trading connections associated
                                with this provider.

                            </p>

                        </div>

                        <button
                            className="rounded-lg bg-slate-900 px-4 py-2 text-white hover:bg-slate-800"
                        >
                            + New Connection
                        </button>

                    </div>

                    <div className="mt-8 overflow-x-auto">

                        <table className="min-w-full">

                            <thead>

                                <tr className="border-b">

                                    <th className="pb-4 text-left">
                                        Connection
                                    </th>

                                    <th className="pb-4 text-left">
                                        Provider
                                    </th>

                                    <th className="pb-4 text-left">
                                        Environment
                                    </th>

                                    <th className="pb-4 text-left">
                                        Status
                                    </th>

                                    <th className="pb-4 text-left">
                                        Verification
                                    </th>

                                    <th className="pb-4 text-left">
                                        Actions
                                    </th>

                                </tr>

                            </thead>

                            <tbody>
                                {connections.length === 0 ? (
                                    <tr>
                                        <td
                                            colSpan={6}
                                            className="py-10 text-center text-slate-500"
                                        >
                                            No desktop connections configured
                                            for this provider.
                                        </td>
                                    </tr>
                                ) : (
                                    connections.map(
                                        (connection) => (
                                            <tr
                                                key={connection.id}
                                                className="border-b"
                                            >
                                                <td className="py-4">
                                                    {connection.connection_name}
                                                </td>

                                                <td>
                                                    {connection.provider}
                                                </td>

                                                <td>
                                                    {connection.environment}
                                                </td>

                                                <td>
                                                    <div className="flex flex-col gap-1">
                                                        <span className="font-medium">
                                                            {connection.status}
                                                        </span>

                                                        <span className="text-sm text-slate-500">
                                                            {connection.health}
                                                        </span>
                                                    </div>
                                                </td>

                                                <td>
                                                    {connection.verified
                                                        ? "Verified"
                                                        : "Pending"}
                                                </td>

                                                <td>
                                                    <div className="flex gap-2">
                                                        <button
                                                            type="button"
                                                            onClick={() =>
                                                                handleVerify(connection)
                                                            }
                                                            disabled={
                                                                verifyingConnectionId ===
                                                                connection.id
                                                            }
                                                            className="rounded-lg border border-blue-500 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 disabled:opacity-50"
                                                        >
                                                            {verifyingConnectionId ===
                                                            connection.id
                                                                ? "Verifying..."
                                                                : connection.verified
                                                                    ? "Re-verify"
                                                                    : "Verify"}
                                                        </button>

                                                        <button
                                                            type="button"
                                                            onClick={() =>
                                                                handleSynchronize(
                                                                    connection,
                                                                )
                                                            }
                                                            disabled={
                                                                synchronizingConnectionId ===
                                                                connection.id
                                                            }
                                                            className="rounded-lg bg-slate-900 px-3 py-1 text-sm text-white hover:bg-slate-800 disabled:opacity-50"
                                                        >
                                                            {synchronizingConnectionId ===
                                                            connection.id
                                                                ? "Synchronizing..."
                                                                : "Synchronize"}
                                                        </button>
                                                    </div>
                                                </td>

                                            </tr>
                                        ),
                                    )
                                )}
                            </tbody>

                        </table>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Desktop Infrastructure */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8">

                    <h2 className="text-3xl font-semibold">

                        Desktop Infrastructure

                    </h2>

                    <p className="mt-2 text-slate-500">

                        Internal desktop acquisition components
                        supporting this provider.

                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-3">

                        <InfrastructureCard
                            title="Connector"
                            status="READY"
                        />

                        <InfrastructureCard
                            title="Translator"
                            status="READY"
                        />

                        <InfrastructureCard
                            title="Normalizer"
                            status="READY"
                        />

                        <InfrastructureCard
                            title="Validator"
                            status="READY"
                        />

                        <InfrastructureCard
                            title="Synchronizer"
                            status="READY"
                        />

                        <InfrastructureCard
                            title="Evidence Adapter"
                            status="READY"
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Diagnostics */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">

                        Diagnostics

                    </h2>

                    <p className="mt-2 text-slate-500">

                        Runtime diagnostics and operational health for this
                        desktop provider.

                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-3">

                        <SummaryCard
                            title="Connection State"
                            value={
                                selectedConnection
                                    ? selectedConnection.status
                                    : "NO CONNECTION"
                            }
                        />

                        <SummaryCard
                            title="Health"
                            value={
                                selectedConnection
                                    ? selectedConnection.health
                                    : "N/A"
                            }
                        />

                        <SummaryCard
                            title="Connected"
                            value={
                                selectedConnection
                                    ? selectedConnection.connected
                                        ? "YES"
                                        : "NO"
                                    : "N/A"
                            }
                        />

                        <SummaryCard
                            title="Verified"
                            value={
                                selectedConnection
                                    ? selectedConnection.verified
                                        ? "YES"
                                        : "NO"
                                    : "N/A"
                            }
                        />

                        <SummaryCard
                            title="Synchronizations Failed"
                            value={
                                selectedConnection
                                    ? String(
                                        selectedConnection.statistics
                                            .failed_synchronizations,
                                    )
                                    : "0"
                            }
                        />

                        <SummaryCard
                            title="Evidence Packages"
                            value={
                                selectedConnection
                                    ? String(
                                        selectedConnection.statistics
                                            .evidence_packages,
                                    )
                                    : "0"
                            }
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Configuration */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Configuration

                            </h2>

                            <p className="mt-2 text-slate-500">

                                Canonical connection configuration currently
                                reported by the Provider Connections runtime.

                            </p>

                        </div>

                        <button
                            className="rounded-lg border px-4 py-2 hover:bg-slate-100"
                        >
                            Edit Configuration
                        </button>

                    </div>

                    <div className="mt-8 grid gap-4 lg:grid-cols-2">

                        <ConfigurationItem
                            title="Connection"
                            value={
                                selectedConnection
                                    ? selectedConnection.connection_name
                                    : "Not configured"
                            }
                        />

                        <ConfigurationItem
                            title="Provider"
                            value={
                                selectedConnection
                                    ? selectedConnection.provider
                                    : providerId
                            }
                        />

                        <ConfigurationItem
                            title="Environment"
                            value={
                                selectedConnection
                                    ? selectedConnection.environment
                                    : "Not configured"
                            }
                        />

                        <ConfigurationItem
                            title="Engine"
                            value="Desktop Trading Engine"
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Connected Accounts */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Connected Accounts

                            </h2>

                            <p className="mt-2 text-slate-500">

                                Trading accounts will appear here when account
                                discovery is exposed by the provider connection runtime.

                            </p>

                        </div>

                        <button
                            className="rounded-lg border px-4 py-2 hover:bg-slate-100"
                        >
                            Refresh Accounts
                        </button>

                    </div>

                    <div className="mt-8 overflow-x-auto">

                        <table className="min-w-full">

                            <thead>

                                <tr className="border-b">

                                    <th className="pb-4 text-left">
                                        Account ID
                                    </th>

                                    <th className="pb-4 text-left">
                                        Broker
                                    </th>

                                    <th className="pb-4 text-left">
                                        Environment
                                    </th>

                                    <th className="pb-4 text-left">
                                        Currency
                                    </th>

                                    <th className="pb-4 text-left">
                                        Status
                                    </th>

                                    <th className="pb-4 text-left">
                                        Last Synchronization
                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                <tr>

                                    <td
                                        colSpan={6}
                                        className="py-12 text-center text-slate-500"
                                    >

                                        No accounts discovered for this
                                        provider.

                                    </td>

                                </tr>

                            </tbody>

                        </table>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Synchronization Center */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">

                        Synchronization Center

                    </h2>

                    <p className="mt-2 text-slate-500">

                        Institutional synchronization pipeline for this
                        desktop provider.

                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-5">

                        <SummaryCard
                            title="Synchronizations"
                            value={
                                selectedConnection
                                    ? String(
                                        selectedConnection.statistics
                                            .synchronization_count,
                                    )
                                    : "0"
                            }
                        />

                        <SummaryCard
                            title="Successful"
                            value={
                                selectedConnection
                                    ? String(
                                        selectedConnection.statistics
                                            .successful_synchronizations,
                                    )
                                    : "0"
                            }
                        />

                        <SummaryCard
                            title="Failed"
                            value={
                                selectedConnection
                                    ? String(
                                        selectedConnection.statistics
                                            .failed_synchronizations,
                                    )
                                    : "0"
                            }
                        />

                        <SummaryCard
                            title="Evidence Packages"
                            value={
                                selectedConnection
                                    ? String(
                                        selectedConnection.statistics
                                            .evidence_packages,
                                    )
                                    : "0"
                            }
                        />

                        <SummaryCard
                            title="Last Sync"
                            value={
                                selectedConnection?.statistics
                                    .last_synchronization
                                    ?? "-"
                            }
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Activity Timeline */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Activity Timeline

                            </h2>

                            <p className="mt-2 text-slate-500">

                                Institutional operational history for this
                                desktop provider.

                            </p>

                        </div>

                        <button
                            className="rounded-lg border px-4 py-2 hover:bg-slate-100"
                        >
                            Refresh Timeline
                        </button>

                    </div>

                    <div className="mt-8">
                        <p className="text-slate-500">
                            Provider activity will appear here when
                            provider-specific activity events are exposed
                            by the runtime.
                        </p>
                    </div>

                </div>

            </div>

        </div>

    );

}

function IdentityCard({

    title,

    value,

}:{

    title:string;

    value:string;

}){

    return(

        <div className="rounded-2xl border bg-white p-6">

            <div className="text-sm text-slate-500">

                {title}

            </div>

            <div className="mt-3 text-2xl font-bold">

                {value}

            </div>

        </div>

    );

}

function SummaryCard({

    title,

    value,

}:{

    title:string;

    value:string;

}){

    return(

        <div className="rounded-xl border bg-slate-50 p-5">

            <div className="text-sm text-slate-500">

                {title}

            </div>

            <div className="mt-3 text-2xl font-bold">

                {value}

            </div>

        </div>

    );

}

function InfrastructureCard({

    title,

    status,

}:{

    title:string;

    status:string;

}){

    return(

        <div className="rounded-xl border bg-slate-50 p-5">

            <div className="font-semibold">

                {title}

            </div>

            <div
                className={`mt-5 inline-flex rounded-full px-3 py-1 text-sm font-semibold ${
                    status === "READY" ||
                    status === "HEALTHY" ||
                    status === "ACTIVE" ||
                    status === "ONLINE"
                        ? "bg-green-100 text-green-700"
                        : status === "REGISTERED" ||
                        status === "VERIFIED"
                            ? "bg-blue-100 text-blue-700"
                            : status === "OFFLINE" ||
                            status === "FAILED" ||
                            status === "UNHEALTHY"
                                ? "bg-amber-100 text-amber-700"
                                : "bg-slate-100 text-slate-700"
                }`}
            >
                {status}
            </div>

        </div>

    );

}

function ConfigurationItem({

    title,

    value,

}:{

    title:string;

    value:string;

}){

    return(

        <div className="rounded-xl border bg-slate-50 p-5">

            <div className="text-sm text-slate-500">

                {title}

            </div>

            <div className="mt-3 font-semibold">

                {value}

            </div>

        </div>

    );

}

function TimelineEvent({

    title,

    description,

    timestamp,

    severity,

}:{

    title:string;

    description:string;

    timestamp:string;

    severity:string;

}){

    return(

        <div className="border-l-4 border-slate-300 pl-5">

            <div className="flex items-center justify-between">

                <div className="font-semibold">

                    {title}

                </div>

                <div className="text-sm text-slate-500">

                    {timestamp}

                </div>

            </div>

            <div className="mt-2 text-slate-600">

                {description}

            </div>

            <div className="mt-3 inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium">

                {severity}

            </div>

        </div>

    );

}