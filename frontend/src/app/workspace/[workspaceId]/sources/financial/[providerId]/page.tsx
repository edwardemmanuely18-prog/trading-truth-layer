"use client";

import Link from "next/link";

import { useParams } from "next/navigation";

import Navbar from "../../../../../../components/Navbar";


export default function FinancialProviderPage() {

    const params = useParams();

    const workspaceId = Number(params.workspaceId);

    const providerId = String(params.providerId);

    const provider = {

        id: providerId,

        name: "Financial Provider",

        engine: "Financial Engine",

        type: "Financial",

        status: "Ready",

        health: "Healthy",

        certification: "Institutional",

        institution: "Not Connected",

        network: "Financial Network",

        environment: "Production",

        version: "1.0.0",

    };

    const summary = {

        connectedServices: 0,

        activeSessions: 0,

        synchronizedRecords: 0,

        pendingTransfers: 0,

        failedTransfers: 0,

        health: "Healthy",

    };

    return (

        <div className="min-h-screen bg-slate-50">

            <Navbar />

            <div className="mx-auto max-w-7xl px-6 py-10">

                {/* ====================================================== */}
                {/* Hero */}
                {/* ====================================================== */}

                <div className="mb-10">

                    <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                        INSTITUTIONAL FINANCIAL PROVIDER

                    </div>

                    <h1 className="mt-2 text-5xl font-bold">

                        {provider.name}

                    </h1>

                    <p className="mt-4 max-w-5xl leading-7 text-slate-600">

                        Institutional financial infrastructure responsible
                        for treasury operations, banking integrations,
                        custodial services, settlement systems and financial
                        evidence acquisition.

                    </p>

                </div>

                {/* ====================================================== */}
                {/* Provider Identity */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Provider Identity

                            </h2>

                            <p className="mt-2 text-slate-500">

                                Canonical identity of the financial
                                institution registered within the Evidence
                                Acquisition Runtime.

                            </p>

                        </div>

                        <Link

                            href={`/workspace/${workspaceId}/sources`}

                            className="rounded-lg border px-4 py-2 hover:bg-slate-100"

                        >

                            Back to Sources

                        </Link>

                    </div>

                    <div className="mt-8 grid gap-4 lg:grid-cols-3">

                        <IdentityItem
                            label="Institution"
                            value={provider.institution}
                        />

                        <IdentityItem
                            label="Engine"
                            value={provider.engine}
                        />

                        <IdentityItem
                            label="Provider Type"
                            value={provider.type}
                        />

                        <IdentityItem
                            label="Certification"
                            value={provider.certification}
                        />

                        <IdentityItem
                            label="Financial Network"
                            value={provider.network}
                        />

                        <IdentityItem
                            label="Environment"
                            value={provider.environment}
                        />

                        <IdentityItem
                            label="Version"
                            value={provider.version}
                        />

                        <IdentityItem
                            label="Status"
                            value={provider.status}
                        />

                        <IdentityItem
                            label="Health"
                            value={provider.health}
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Operational Summary */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">

                        Operational Summary

                    </h2>

                    <p className="mt-2 text-slate-500">

                        Real-time operational overview of the institutional
                        financial provider.

                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-6">

                        <SummaryCard
                            title="Connected Services"
                            value={summary.connectedServices}
                        />

                        <SummaryCard
                            title="Active Sessions"
                            value={summary.activeSessions}
                        />

                        <SummaryCard
                            title="Synchronized Records"
                            value={summary.synchronizedRecords}
                        />

                        <SummaryCard
                            title="Pending Transfers"
                            value={summary.pendingTransfers}
                        />

                        <SummaryCard
                            title="Failed Transfers"
                            value={summary.failedTransfers}
                        />

                        <SummaryCard
                            title="Health"
                            value={summary.health}
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Financial Infrastructure */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">

                        Financial Infrastructure

                    </h2>

                    <p className="mt-2 text-slate-500">

                        Institutional financial systems available through
                        this provider.

                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-2">

                        <InfrastructureCard

                            title="Banking Services"

                            description="Institutional banking connectivity and account infrastructure."

                            status="READY"

                        />

                        <InfrastructureCard

                            title="Custody"

                            description="Asset custody and safekeeping infrastructure."

                            status="READY"

                        />

                        <InfrastructureCard

                            title="Treasury"

                            description="Cash management, liquidity and treasury operations."

                            status="READY"

                        />

                        <InfrastructureCard

                            title="Settlement"

                            description="Settlement and clearing infrastructure."

                            status="READY"

                        />

                        <InfrastructureCard

                            title="Payment Rails"

                            description="Domestic and international payment networks."

                            status="READY"

                        />

                        <InfrastructureCard

                            title="SWIFT Network"

                            description="Institutional financial messaging infrastructure."

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

                        Operational diagnostics for institutional financial
                        connectivity, treasury infrastructure and settlement
                        systems.

                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-3">

                        <DiagnosticCard
                            title="Connectivity"
                            value="Healthy"
                        />

                        <DiagnosticCard
                            title="Authentication"
                            value="Operational"
                        />

                        <DiagnosticCard
                            title="Treasury Services"
                            value="Available"
                        />

                        <DiagnosticCard
                            title="Settlement Network"
                            value="Operational"
                        />

                        <DiagnosticCard
                            title="SWIFT Messaging"
                            value="Ready"
                        />

                        <DiagnosticCard
                            title="Evidence Acquisition"
                            value="Idle"
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

                                Financial provider configuration used by the
                                Evidence Acquisition Runtime.

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
                            label="Institution"
                            value={provider.institution}
                        />

                        <ConfigurationItem
                            label="Financial Network"
                            value={provider.network}
                        />

                        <ConfigurationItem
                            label="Environment"
                            value={provider.environment}
                        />

                        <ConfigurationItem
                            label="Certification"
                            value={provider.certification}
                        />

                        <ConfigurationItem
                            label="Status"
                            value={provider.status}
                        />

                        <ConfigurationItem
                            label="Version"
                            value={provider.version}
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Connected Financial Services */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Connected Financial Services

                            </h2>

                            <p className="mt-2 text-slate-500">

                                Financial services discovered through this
                                institutional provider and available for
                                evidence acquisition.

                            </p>

                        </div>

                        <button
                            className="rounded-lg border px-4 py-2 hover:bg-slate-100"
                        >

                            Refresh Services

                        </button>

                    </div>

                    <div className="mt-8 overflow-x-auto">

                        <table className="min-w-full">

                            <thead>

                                <tr className="border-b">

                                    <th className="pb-4 text-left">

                                        Service

                                    </th>

                                    <th className="pb-4 text-left">

                                        Category

                                    </th>

                                    <th className="pb-4 text-left">

                                        Environment

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
                                        colSpan={5}
                                        className="py-12 text-center text-slate-500"
                                    >

                                        No financial services discovered.

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

                        Financial evidence synchronization across banking,
                        treasury, settlement and custodial systems.

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

                                        Financial Service

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

                <div className="rounded-2xl border bg-white p-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Activity Timeline

                            </h2>

                            <p className="mt-2 text-slate-500">

                                Chronological operational history for this
                                institutional financial provider.

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

                            title="Financial Provider Registered"

                            description="Financial provider registered with the Evidence Acquisition Runtime."

                            timestamp="-"

                            severity="Information"

                        />

                        <TimelineEvent

                            title="Waiting for Financial Services"

                            description="No financial services have been discovered."

                            timestamp="-"

                            severity="Pending"

                        />

                        <TimelineEvent

                            title="Waiting for Synchronization"

                            description="Financial synchronization will begin after services become available."

                            timestamp="-"

                            severity="Pending"

                        />

                        <TimelineEvent

                            title="Waiting for Evidence Acquisition"

                            description="Evidence acquisition will begin after successful synchronization."

                            timestamp="-"

                            severity="Pending"

                        />

                    </div>

                </div>

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

            <div className="mt-2 text-3xl font-bold">

                {value}

            </div>

        </div>

    );

}

function IdentityItem({
    label,
    value,
}: {
    label: string;
    value: string;
}) {

    return (

        <div className="rounded-xl border bg-slate-50 p-5">

            <div className="text-sm text-slate-500">

                {label}

            </div>

            <div className="mt-2 font-semibold">

                {value}

            </div>

        </div>

    );

}

function InfrastructureCard({
    title,
    description,
    status,
}: {
    title: string;
    description: string;
    status: string;
}) {

    return (

        <div className="rounded-xl border bg-slate-50 p-6">

            <div className="flex items-center justify-between">

                <h3 className="text-lg font-semibold">

                    {title}

                </h3>

                <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">

                    {status}

                </span>

            </div>

            <p className="mt-4 text-sm leading-6 text-slate-600">

                {description}

            </p>

        </div>

    );

}

function DiagnosticCard({
    title,
    value,
}: {
    title: string;
    value: string;
}) {

    return (

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

function ConfigurationItem({
    label,
    value,
}: {
    label: string;
    value: string;
}) {

    return (

        <div className="rounded-xl border bg-slate-50 p-5">

            <div className="text-sm text-slate-500">

                {label}

            </div>

            <div className="mt-3 font-medium break-all">

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