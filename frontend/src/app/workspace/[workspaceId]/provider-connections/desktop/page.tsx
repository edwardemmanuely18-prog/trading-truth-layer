"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import Navbar from "../../../../../components/Navbar";

import {
    getEvidenceAcquisitionOverview,
    type EvidenceAcquisitionOverview,
} from "../../../../../lib/api";

export default function DesktopTradingEnginePage() {

    const workspaceId = 1;

    const [overview, setOverview] =
        useState<EvidenceAcquisitionOverview | null>(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState<string | null>(null);

    useEffect(() => {

        let mounted = true;

        async function loadOverview() {

            try {

                setLoading(true);

                const data =
                    await getEvidenceAcquisitionOverview(
                        workspaceId,
                    );

                if (mounted) {

                    setOverview(data);

                    setError(null);

                }

            } catch (err) {

                if (mounted) {

                    setError(

                        err instanceof Error
                            ? err.message
                            : "Unable to load Desktop Runtime.",

                    );

                }

            } finally {

                if (mounted) {

                    setLoading(false);

                }

            }

        }

        loadOverview();

        return () => {

            mounted = false;

        };

    }, [workspaceId]);

    return (

        <div className="min-h-screen bg-slate-50">

            <Navbar />

            <div className="mx-auto max-w-7xl px-6 py-10">

                {/* ====================================================== */}
                {/* Hero */}
                {/* ====================================================== */}

                <div className="mb-10">

                    <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                        EVIDENCE ACQUISITION ENGINE

                    </div>

                    <div className="mt-3 flex items-center justify-between">

                        <div>

                            <h1 className="text-5xl font-bold text-slate-900">

                                Desktop Trading Engine

                            </h1>

                            <p className="mt-5 max-w-5xl text-slate-600 leading-8">

                                Canonical evidence acquisition engine responsible
                                for synchronizing institutional desktop trading
                                evidence from supported trading platforms into
                                the Trading Truth Layer Evidence Acquisition
                                Runtime. The engine provides a unified
                                synchronization pipeline for desktop trading
                                providers while exposing a single canonical
                                evidence model to the remainder of the
                                Trading Truth Layer platform.

                            </p>

                        </div>

                        <div className="rounded-2xl border bg-white px-8 py-6 shadow-sm">

                            <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">

                                Runtime Status

                            </div>

                            <div className="mt-4 flex items-center gap-3">

                                <div
                                    className={`h-3 w-3 rounded-full animate-pulse ${
                                        loading
                                            ? "bg-amber-500"
                                            : error
                                            ? "bg-red-500"
                                            : "bg-green-500"
                                    }`}
                                />

                                <span className="text-lg font-semibold text-slate-900">

                                    {loading
                                        ? "Loading..."
                                        : error
                                        ? "Unavailable"
                                        : overview?.runtime.state ?? "Unknown"}

                                </span>

                            </div>

                            <div className="mt-3 text-sm text-slate-500">

                                {loading
                                    ? "Loading runtime telemetry..."
                                    : error
                                    ? error
                                    : "Runtime telemetry synchronized."}

                            </div>

                        </div>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Executive Runtime Metrics */}
                {/* ====================================================== */}

                <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-6 mb-10">

                    <EngineMetricCard
                        title="Supported Providers"
                        value="0"
                        subtitle="Desktop platforms"
                    />

                    <EngineMetricCard
                        title="Configured Connections"
                        value="0"
                        subtitle="Workspace connections"
                    />

                    <EngineMetricCard
                        title="Healthy Connections"
                        value="0"
                        subtitle="Operational"
                    />

                    <EngineMetricCard
                        title="Synchronizations"
                        value="0"
                        subtitle="Running"
                    />

                    <EngineMetricCard
                        title="Evidence Packages"
                        value="0"
                        subtitle="Generated"
                    />

                    <EngineMetricCard
                        title="Runtime State"
                        value="READY"
                        subtitle="Engine lifecycle"
                    />

                </div>

                {/* ====================================================== */}
                {/* Engine Health */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-10">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Engine Health

                            </h2>

                            <p className="mt-2 text-slate-500">

                                Institutional runtime health of the Desktop
                                Trading Engine and its core operational
                                components responsible for evidence
                                acquisition.

                            </p>

                        </div>

                    </div>

                    <div className="mt-8 grid gap-5 lg:grid-cols-2 xl:grid-cols-3">

                        <HealthCard
                            component="Runtime"
                            status="READY"
                            description="Evidence Acquisition Runtime is operational."
                        />

                        <HealthCard
                            component="Provider Registry"
                            status="READY"
                            description="Desktop provider catalog successfully loaded."
                        />

                        <HealthCard
                            component="Connector Factory"
                            status="READY"
                            description="Connector construction infrastructure available."
                        />

                        <HealthCard
                            component="Synchronization Pipeline"
                            status="READY"
                            description="Synchronization pipeline ready for acquisition."
                        />

                        <HealthCard
                            component="Translation Pipeline"
                            status="READY"
                            description="Canonical evidence translation pipeline operational."
                        />

                        <HealthCard
                            component="Evidence Pipeline"
                            status="READY"
                            description="Canonical evidence publication pipeline available."
                        />

                    </div>

                </div>

                                {/* ====================================================== */}
                {/* Evidence Categories */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-10">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Canonical Evidence Categories

                            </h2>

                            <p className="mt-2 max-w-4xl text-slate-500">

                                The Desktop Trading Engine synchronizes a
                                standardized set of institutional evidence
                                categories from supported desktop trading
                                platforms. Every provider is translated into
                                these canonical evidence models before entering
                                the Trading Truth Layer Evidence Acquisition
                                Runtime.

                            </p>

                        </div>

                    </div>

                    <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-4">

                        <EvidenceCategoryCard
                            title="Trading Evidence"
                            items={[
                                "Trades",
                                "Orders",
                                "Deals",
                                "Positions",
                            ]}
                        />

                        <EvidenceCategoryCard
                            title="Account Evidence"
                            items={[
                                "Account",
                                "Balance",
                                "Equity",
                                "Margin",
                            ]}
                        />

                        <EvidenceCategoryCard
                            title="Infrastructure Evidence"
                            items={[
                                "Broker",
                                "Server",
                                "Terminal",
                                "User",
                            ]}
                        />

                        <EvidenceCategoryCard
                            title="Market Evidence"
                            items={[
                                "Symbols",
                                "Prices",
                                "Activity",
                                "History",
                            ]}
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Supported Desktop Providers */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-10">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Supported Desktop Providers

                            </h2>

                            <p className="mt-2 max-w-4xl text-slate-500">

                                Select a supported desktop trading platform to create an
                                authenticated provider connection. Each provider is
                                translated into the canonical Desktop Evidence Model before
                                entering the Evidence Acquisition Runtime.

                            </p>

                        </div>

                    </div>

                    <div className="mt-8 grid gap-6 lg:grid-cols-2 xl:grid-cols-3">

                        <DesktopProviderCard
                            workspaceId={workspaceId}
                            provider="MetaTrader 5"
                            adapter="MT5 Adapter"
                            status="SUPPORTED"
                        />

                        <DesktopProviderCard
                            workspaceId={workspaceId}
                            provider="MetaTrader 4"
                            adapter="MT4 Adapter"
                            status="SUPPORTED"
                        />

                        <DesktopProviderCard
                            workspaceId={workspaceId}
                            provider="cTrader"
                            adapter="cTrader Adapter"
                            status="SUPPORTED"
                        />

                        <DesktopProviderCard
                            workspaceId={workspaceId}
                            provider="NinjaTrader"
                            adapter="NinjaTrader Adapter"
                            status="SUPPORTED"
                        />

                        <DesktopProviderCard
                            workspaceId={workspaceId}
                            provider="TradeStation"
                            adapter="TradeStation Adapter"
                            status="SUPPORTED"
                        />

                        <DesktopProviderCard
                            workspaceId={workspaceId}
                            provider="MotiveWave"
                            adapter="MotiveWave Adapter"
                            status="SUPPORTED"
                        />

                        <DesktopProviderCard
                            workspaceId={workspaceId}
                            provider="MultiCharts"
                            adapter="MultiCharts Adapter"
                            status="SUPPORTED"
                        />

                        <DesktopProviderCard
                            workspaceId={workspaceId}
                            provider="Quantower"
                            adapter="Quantower Adapter"
                            status="SUPPORTED"
                        />

                        <DesktopProviderCard
                            workspaceId={workspaceId}
                            provider="Sierra Chart"
                            adapter="Sierra Chart Adapter"
                            status="SUPPORTED"
                        />

                        <DesktopProviderCard
                            workspaceId={workspaceId}
                            provider="Trading Technologies"
                            adapter="Trading Technologies Adapter"
                            status="SUPPORTED"
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Synchronization Profiles */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-10">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Synchronization Profiles

                            </h2>

                            <p className="mt-2 max-w-5xl text-slate-500">

                                Define which categories of canonical evidence will be
                                synchronized when creating a provider connection.
                                Profiles standardize evidence acquisition across all
                                supported desktop trading platforms.

                            </p>

                        </div>

                    </div>

                    <div className="mt-8 grid gap-6 lg:grid-cols-2">

                        <SynchronizationProfileCard
                            title="Complete Verification"
                            description="Acquire every canonical evidence category required for institutional verification."
                            selected
                        />

                        <SynchronizationProfileCard
                            title="Performance Analytics"
                            description="Acquire only performance-related evidence."
                        />

                        <SynchronizationProfileCard
                            title="Risk Monitoring"
                            description="Acquire balance, equity, margin and exposure evidence."
                        />

                        <SynchronizationProfileCard
                            title="Custom Profile"
                            description="Select individual evidence categories."
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Active Desktop Connections */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-10">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Active Desktop Connections

                            </h2>

                            <p className="mt-2 max-w-4xl text-slate-500">

                                Institutional view of configured desktop
                                provider connections participating in the
                                Evidence Acquisition Runtime.

                            </p>

                        </div>

                    </div>

                    <div className="mt-8 overflow-x-auto">

                        <table className="min-w-full">

                            <thead>

                                <tr className="border-b text-left text-sm uppercase tracking-wide text-slate-500">

                                    <th className="px-4 py-4">
                                        Connection
                                    </th>

                                    <th className="px-4 py-4">
                                        Provider
                                    </th>

                                    <th className="px-4 py-4">
                                        Account
                                    </th>

                                    <th className="px-4 py-4">
                                        Environment
                                    </th>

                                    <th className="px-4 py-4">
                                        Status
                                    </th>

                                    <th className="px-4 py-4">
                                        Synchronization
                                    </th>

                                    <th className="px-4 py-4">
                                        Actions
                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                <EmptyDesktopConnectionRow />

                            </tbody>

                        </table>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Synchronization Jobs */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-10">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Synchronization Jobs

                            </h2>

                            <p className="mt-2 max-w-4xl text-slate-500">

                                Operational synchronization queue executed by the
                                Desktop Trading Engine. Every acquisition session is
                                tracked from scheduling through evidence publication.

                            </p>

                        </div>

                    </div>

                    <div className="mt-8 overflow-x-auto">

                        <table className="min-w-full">

                            <thead>

                                <tr className="border-b text-left text-sm uppercase tracking-wide text-slate-500">

                                    <th className="px-4 py-4">
                                        Job
                                    </th>

                                    <th className="px-4 py-4">
                                        Provider
                                    </th>

                                    <th className="px-4 py-4">
                                        Connection
                                    </th>

                                    <th className="px-4 py-4">
                                        Status
                                    </th>

                                    <th className="px-4 py-4">
                                        Progress
                                    </th>

                                    <th className="px-4 py-4">
                                        Started
                                    </th>

                                    <th className="px-4 py-4">
                                        Actions
                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                <EmptySynchronizationRow />

                            </tbody>

                        </table>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Recent Engine Activity */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-10">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Recent Engine Activity

                            </h2>

                            <p className="mt-2 max-w-4xl text-slate-500">

                                Institutional operational timeline showing
                                connection lifecycle events, synchronization
                                execution, evidence acquisition and runtime
                                activities performed by the Desktop Trading
                                Engine.

                            </p>

                        </div>

                    </div>

                    <div className="mt-8">

                        <EmptyActivityTimeline />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Engine Diagnostics */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-10">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Engine Diagnostics

                            </h2>

                            <p className="mt-2 max-w-5xl text-slate-500">

                                Institutional runtime diagnostics exposing the
                                operational state of the Desktop Trading Engine,
                                connector infrastructure, provider registry and
                                synchronization pipeline.

                            </p>

                        </div>

                        <button
                            className="rounded-lg border px-5 py-3 text-sm font-medium hover:bg-slate-100"
                        >

                            Refresh Diagnostics

                        </button>

                    </div>

                    <div className="mt-8 grid gap-6 lg:grid-cols-2">

                        <DiagnosticCard
                            title="Runtime"
                            rows={[
                                ["State", "READY"],
                                ["Version", "1.0.0"],
                                ["Registered Engines", "1"],
                                ["Running Engines", "1"],
                            ]}
                        />

                        <DiagnosticCard
                            title="Provider Registry"
                            rows={[
                                ["Registered Providers", "0"],
                                ["Healthy Providers", "0"],
                                ["Failed Providers", "0"],
                                ["Synchronization Queue", "0"],
                            ]}
                        />

                        <DiagnosticCard
                            title="Connector Infrastructure"
                            rows={[
                                ["Connector Factory", "READY"],
                                ["Translation Pipeline", "READY"],
                                ["Synchronization Pipeline", "READY"],
                                ["Evidence Pipeline", "READY"],
                            ]}
                        />

                        <DiagnosticCard
                            title="Evidence Runtime"
                            rows={[
                                ["Evidence Packages", "0"],
                                ["Published Packages", "0"],
                                ["Verification Queue", "0"],
                                ["Last Synchronization", "--"],
                            ]}
                        />

                    </div>

                </div>

            </div>

        </div>

    );

}

function EngineMetricCard({
    title,
    value,
    subtitle,
}: {
    title: string;
    value: string | number;
    subtitle: string;
}) {

    return (

        <div className="rounded-2xl border bg-white p-6 shadow-sm">

            <div className="text-sm font-medium text-slate-500">

                {title}

            </div>

            <div className="mt-3 text-4xl font-bold text-slate-900">

                {value}

            </div>

            <div className="mt-3 text-sm text-slate-500">

                {subtitle}

            </div>

        </div>

    );

}

function HealthCard({
    component,
    status,
    description,
}: {
    component: string;
    status: string;
    description: string;
}) {

    const healthy = status === "READY";

    return (

        <div className="rounded-2xl border bg-slate-50 p-6">

            <div className="flex items-center justify-between">

                <div>

                    <div className="text-lg font-semibold text-slate-900">

                        {component}

                    </div>

                </div>

                <div
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        healthy
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                    }`}
                >

                    {status}

                </div>

            </div>

            <div className="mt-5 text-sm leading-6 text-slate-600">

                {description}

            </div>

        </div>

    );

}

function EvidenceCategoryCard({
    title,
    items,
}: {
    title: string;
    items: string[];
}) {

    return (

        <div className="rounded-2xl border bg-slate-50 p-6">

            <div className="text-xl font-semibold text-slate-900">

                {title}

            </div>

            <div className="mt-5 space-y-3">

                {items.map((item) => (

                    <div
                        key={item}
                        className="flex items-center gap-3"
                    >

                        <div className="h-2 w-2 rounded-full bg-green-500" />

                        <span className="text-sm text-slate-700">

                            {item}

                        </span>

                    </div>

                ))}

            </div>

        </div>

    );

}

function DesktopProviderCard({

    workspaceId,

    provider,

    adapter,

    status,

}: {

    workspaceId: number;

    provider: string;

    adapter: string;

    status: string;

}) {

    const router = useRouter();

    function handleCreateConnection() {

        router.push(

            `/workspace/${workspaceId}/provider-connections/desktop/new?provider=${encodeURIComponent(provider)}`,

        );

    }

    return (

        <div className="rounded-2xl border bg-slate-50 p-6">

            <div className="flex items-center justify-between">

                <div>

                    <div className="text-xl font-semibold text-slate-900">

                        {provider}

                    </div>

                    <div className="mt-2 text-sm text-slate-500">

                        {adapter}

                    </div>

                </div>

                <div className="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">

                    {status}

                </div>

            </div>

            <div className="mt-6 text-sm leading-6 text-slate-600">

                Synchronize canonical desktop trading evidence including
                trades, orders, positions, account information and market
                activity through the Desktop Trading Engine.

            </div>

            <button

                onClick={handleCreateConnection}

                className="mt-6 w-full rounded-lg bg-slate-900 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800"

            >

                Create Connection

            </button>

        </div>

    );

}

function EmptyDesktopConnectionRow() {

    return (

        <tr>

            <td
                colSpan={7}
                className="px-6 py-16 text-center"
            >

                <div className="mx-auto max-w-2xl">

                    <div className="text-xl font-semibold text-slate-900">

                        No Desktop Connections

                    </div>

                    <p className="mt-3 text-slate-500 leading-7">

                        No desktop trading platforms have been connected to
                        this workspace.

                        Create your first authenticated provider connection
                        above to begin synchronizing canonical desktop
                        trading evidence into the Trading Truth Layer
                        Evidence Acquisition Runtime.

                    </p>

                </div>

            </td>

        </tr>

    );

}

function SynchronizationProfileCard({
    title,
    description,
    selected = false,
}: {
    title: string;
    description: string;
    selected?: boolean;
}) {

    return (

        <div
            className={`rounded-2xl border p-6 transition ${
                selected
                    ? "border-slate-900 bg-slate-100"
                    : "bg-slate-50"
            }`}
        >

            <div className="flex items-center justify-between">

                <div>

                    <div className="text-xl font-semibold">

                        {title}

                    </div>

                    <div className="mt-3 text-sm leading-6 text-slate-600">

                        {description}

                    </div>

                </div>

                <button
                    className={`rounded-lg px-4 py-2 text-sm font-medium ${
                        selected
                            ? "bg-slate-900 text-white"
                            : "border bg-white hover:bg-slate-100"
                    }`}
                >

                    {selected ? "Selected" : "Select"}

                </button>

            </div>

        </div>

    );

}

function EmptySynchronizationRow() {

    return (

        <tr>

            <td
                colSpan={7}
                className="px-6 py-16 text-center"
            >

                <div className="mx-auto max-w-2xl">

                    <div className="text-xl font-semibold text-slate-900">

                        No Synchronization Jobs

                    </div>

                    <p className="mt-3 text-slate-500 leading-7">

                        No synchronization sessions have been executed by
                        the Desktop Trading Engine.

                        Create a provider connection and begin evidence
                        acquisition to monitor synchronization activity.

                    </p>

                </div>

            </td>

        </tr>

    );

}

function EmptyActivityTimeline() {

    return (

        <div className="rounded-xl border border-dashed p-12 text-center">

            <div className="text-xl font-semibold text-slate-900">

                No Engine Activity

            </div>

            <p className="mt-4 max-w-3xl mx-auto text-slate-500 leading-7">

                The Desktop Trading Engine has not yet processed any
                provider connection events, synchronization requests,
                evidence acquisition sessions or runtime operations.

                Engine activity will automatically appear once provider
                connections begin operating.

            </p>

        </div>

    );

}

function DiagnosticCard({
    title,
    rows,
}: {
    title: string;
    rows: [string, string][];
}) {

    return (

        <div className="rounded-2xl border bg-slate-50 p-6">

            <div className="text-xl font-semibold text-slate-900">

                {title}

            </div>

            <div className="mt-6 space-y-4">

                {rows.map(([label, value]) => (

                    <div
                        key={label}
                        className="flex items-center justify-between border-b pb-3 last:border-0 last:pb-0"
                    >

                        <span className="text-sm text-slate-500">

                            {label}

                        </span>

                        <span className="font-medium text-slate-900">

                            {value}

                        </span>

                    </div>

                ))}

            </div>

        </div>

    );

}