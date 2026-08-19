"use client";

import { useEffect, useState } from "react";

import { useParams } from "next/navigation";

import Navbar from "../../../../../../components/Navbar";

import {
    EvidenceAcquisitionSource,
    getEvidenceAcquisitionSources,
} from "../../../../../../lib/api";

export default function GatewayProviderPage() {

    const params = useParams();

    const workspaceId = Number(params.workspaceId);

    const providerId = String(params.providerId);

    const [loading, setLoading] = useState(true);

    const [provider, setProvider] =
        useState<EvidenceAcquisitionSource | null>(null);

    useEffect(() => {

        async function load() {

            try {

                const providers =
                    await getEvidenceAcquisitionSources(
                        workspaceId,
                    );

                const match =
                    providers.find(

                        (provider) =>

                            provider.name.toLowerCase() ===
                            providerId.toLowerCase()

                    ) ?? null;

                setProvider(match);

            } finally {

                setLoading(false);

            }

        }

        load();

    }, [
        workspaceId,
        providerId,
    ]);

    if (loading) {

        return (

            <div className="min-h-screen bg-slate-50">

                <Navbar />

                <div className="mx-auto max-w-7xl px-6 py-12">

                    <div className="rounded-2xl border bg-white p-10">

                        Loading gateway provider...

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

                        GATEWAY PROVIDER

                    </div>

                    <h1 className="mt-2 text-5xl font-bold">

                        {provider?.name ?? providerId.toUpperCase()}

                    </h1>

                    <p className="mt-4 max-w-5xl leading-7 text-slate-600">

                        Canonical gateway provider responsible for institutional
                        evidence acquisition through Broker APIs, REST services,
                        FIX sessions, WebSocket feeds, exchange connectivity,
                        and future gateway infrastructures operating inside the
                        Evidence Acquisition Runtime.

                    </p>

                </div>

                {/* ====================================================== */}
                {/* Provider Identity */}
                {/* ====================================================== */}

                <div className="grid gap-4 md:grid-cols-4 mb-8">

                    <IdentityCard
                        title="Workspace"
                        value={workspaceId}
                    />

                    <IdentityCard
                        title="Provider"
                        value={provider?.name ?? providerId}
                    />

                    <IdentityCard
                        title="Engine"
                        value="Gateway Engine"
                    />

                    <IdentityCard
                        title="Runtime"
                        value={
                            provider?.active
                                ? "CONNECTED"
                                : "READY"
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

                        High-level operational metrics for this gateway
                        provider.

                    </p>

                <div className="mt-8 grid gap-4 lg:grid-cols-6">

                    <SummaryCard
                        title="Connections"
                        value="0"
                    />

                    <SummaryCard
                        title="Endpoints"
                        value="0"
                    />

                    <SummaryCard
                        title="Synchronizations"
                        value="0"
                    />

                    <SummaryCard
                        title="Evidence"
                        value="0"
                    />

                    <SummaryCard
                        title="Latency"
                        value="-"
                    />

                    <SummaryCard
                        title="Health"
                        value={
                            provider?.active
                                ? "HEALTHY"
                                : "READY"
                        }
                    />

                </div>

                {/* ====================================================== */}
                {/* Gateway Connections */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Gateway Connections

                            </h2>

                            <p className="mt-2 text-slate-500">

                                Gateway connections responsible for acquiring
                                evidence from broker APIs, exchanges and
                                institutional gateway infrastructures.

                            </p>

                        </div>

                        <button
                            className="rounded-lg bg-slate-900 px-4 py-2 text-white hover:bg-slate-800"
                        >

                            + New Gateway Connection

                        </button>

                    </div>

                <div className="mt-8 overflow-x-auto">

                    <table className="min-w-full">

                        <thead>

                            <tr className="border-b">

                                <th className="pb-4 text-left">

                                    Endpoint

                                </th>

                                <th className="pb-4 text-left">

                                    Protocol

                                </th>

                                <th className="pb-4 text-left">

                                    Environment

                                </th>

                                <th className="pb-4 text-left">

                                    Authentication

                                </th>

                                <th className="pb-4 text-left">

                                    Status

                                </th>

                                <th className="pb-4 text-left">

                                    Last Heartbeat

                                </th>

                            </tr>

                        </thead>

                        <tbody>

                            <tr>

                                <td
                                    colSpan={6}
                                    className="py-10 text-center text-slate-500"
                                >

                                    No gateway connections configured.

                                </td>

                            </tr>

                        </tbody>

                    </table>

                </div>

                {/* ====================================================== */}
                {/* Gateway Infrastructure */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">

                        Gateway Infrastructure

                    </h2>

                    <p className="mt-2 text-slate-500">

                        Canonical networking infrastructure responsible for
                        secure institutional communication with broker APIs,
                        exchanges and external acquisition providers.

                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-3">

                        <InfrastructureCard
                            title="REST Client"
                            status="READY"
                        />

                        <InfrastructureCard
                            title="FIX Client"
                            status="READY"
                        />

                        <InfrastructureCard
                            title="WebSocket Client"
                            status="READY"
                        />

                        <InfrastructureCard
                            title="Authentication"
                            status="READY"
                        />

                        <InfrastructureCard
                            title="Gateway Synchronizer"
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

                        Operational health, connectivity diagnostics and runtime
                        status for this gateway provider.

                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-3">

                        <SummaryCard
                            title="Runtime"
                            value="READY"
                        />

                        <SummaryCard
                            title="Heartbeat"
                            value="ONLINE"
                        />

                        <SummaryCard
                            title="Latency"
                            value="-"
                        />

                        <SummaryCard
                            title="Warnings"
                            value="0"
                        />

                        <SummaryCard
                            title="Errors"
                            value="0"
                        />

                        <SummaryCard
                            title="Gateway Version"
                            value="1.0"
                        />

                    </div>

                    <div className="mt-10 overflow-x-auto">

                        <table className="min-w-full">

                            <thead>

                                <tr className="border-b">

                                    <th className="pb-4 text-left">

                                        Component

                                    </th>

                                    <th className="pb-4 text-left">

                                        Status

                                    </th>

                                    <th className="pb-4 text-left">

                                        Last Check

                                    </th>

                                    <th className="pb-4 text-left">

                                        Details

                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                <tr>

                                    <td
                                        colSpan={4}
                                        className="py-10 text-center text-slate-500"
                                    >

                                        No diagnostics available.

                                    </td>

                                </tr>

                            </tbody>

                        </table>

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

                                Runtime configuration governing gateway
                                connectivity, authentication, synchronization
                                and operational policies.

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
                            title="Authentication Method"
                            value="API Key"
                        />

                        <ConfigurationItem
                            title="Auto Synchronization"
                            value="Enabled"
                        />

                        <ConfigurationItem
                            title="Retry Policy"
                            value="Exponential Backoff"
                        />

                        <ConfigurationItem
                            title="Rate Limiting"
                            value="Automatic"
                        />

                        <ConfigurationItem
                            title="Synchronization Interval"
                            value="30 Seconds"
                        />

                        <ConfigurationItem
                            title="Transport Protocol"
                            value="Automatic"
                        />

                    </div>

                </div> 

                {/* ====================================================== */}
                {/* Connected Endpoints */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Connected Endpoints

                            </h2>

                            <p className="mt-2 text-slate-500">

                                Endpoints discovered through registered
                                gateway connections and currently available
                                for institutional evidence acquisition.

                            </p>

                        </div>

                        <button
                            className="rounded-lg border px-4 py-2 hover:bg-slate-100"
                        >

                            Refresh Endpoints

                        </button>

                    </div>

                    <div className="mt-8 overflow-x-auto">

                        <table className="min-w-full">

                            <thead>

                                <tr className="border-b">

                                    <th className="pb-4 text-left">

                                        Endpoint

                                    </th>

                                    <th className="pb-4 text-left">

                                        Protocol

                                    </th>

                                    <th className="pb-4 text-left">

                                        Authentication

                                    </th>

                                    <th className="pb-4 text-left">

                                        Environment

                                    </th>

                                    <th className="pb-4 text-left">

                                        Status

                                    </th>

                                    <th className="pb-4 text-left">

                                        Last Heartbeat

                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                <tr>

                                    <td
                                        colSpan={6}
                                        className="py-12 text-center text-slate-500"
                                    >

                                        No gateway endpoints discovered.

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

                        Institutional synchronization pipeline responsible for
                        acquiring evidence from connected gateway endpoints.

                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-5">

                        <SummaryCard
                            title="Running"
                            value="0"
                        />

                        <SummaryCard
                            title="Queued"
                            value="0"
                        />

                        <SummaryCard
                            title="Completed"
                            value="0"
                        />

                        <SummaryCard
                            title="Failed"
                            value="0"
                        />

                        <SummaryCard
                            title="Last Sync"
                            value="-"
                        />

                    </div>

                    <div className="mt-10 overflow-x-auto">

                        <table className="min-w-full">

                            <thead>

                                <tr className="border-b">

                                    <th className="pb-4 text-left">

                                        Job

                                    </th>

                                    <th className="pb-4 text-left">

                                        Endpoint

                                    </th>

                                    <th className="pb-4 text-left">

                                        Status

                                    </th>

                                    <th className="pb-4 text-left">

                                        Progress

                                    </th>

                                    <th className="pb-4 text-left">

                                        Started

                                    </th>

                                    <th className="pb-4 text-left">

                                        Completed

                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                <tr>

                                    <td
                                        colSpan={6}
                                        className="py-12 text-center text-slate-500"
                                    >

                                        No synchronization jobs available.

                                    </td>

                                </tr>

                            </tbody>

                        </table>

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

                                Chronological operational history for this
                                gateway provider.

                            </p>

                        </div>

                        <button
                            className="rounded-lg border px-4 py-2 hover:bg-slate-100"
                        >

                            Refresh Timeline

                        </button>

                    </div>

                    <div className="mt-8 space-y-6">

                        <TimelineEvent

                            title="Gateway Provider Registered"

                            description="Gateway provider has been registered with the Evidence Acquisition Runtime."

                            timestamp="-"

                            severity="Information"

                        />

                        <TimelineEvent

                            title="Waiting for Gateway Connections"

                            description="No gateway connections have been configured."

                            timestamp="-"

                            severity="Pending"

                        />

                        <TimelineEvent

                            title="Waiting for Endpoint Discovery"

                            description="Connected endpoints will appear after successful gateway connectivity."

                            timestamp="-"

                            severity="Pending"

                        />

                        <TimelineEvent

                            title="Waiting for Synchronization"

                            description="Synchronization begins after endpoint discovery."

                            timestamp="-"

                            severity="Pending"

                        />

                    </div>

                    </div>

                </div>

            </div>

            </div>

        </div>

    );

}


function IdentityCard({
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

            <div className="mt-2 text-2xl font-semibold break-words">

                {value}

            </div>

        </div>

    );

}

function SummaryCard({
    title,
    value,
}: {
    title: string;
    value: string | number;
}) {

    return (

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

            <div className="mt-5 inline-flex rounded-full bg-green-100 px-3 py-1 text-sm font-semibold text-green-700">

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