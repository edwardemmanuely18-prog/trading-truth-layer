"use client";

import Navbar from "../../../../components/Navbar";

import { useEffect, useState } from "react";

import Link from "next/link";

import {
    getEvidenceAcquisitionOverview,
    getEvidenceAcquisitionSources,
    EvidenceAcquisitionSource,
    EvidenceAcquisitionOverview,
} from "../../../../lib/api";

import { useParams } from "next/navigation";

const ENGINE_ROUTE_MAP: Record<string, string> = {
    gateway: "gateway",
    gateway_trading_engine: "gateway",
    desktop: "desktop",
    desktop_trading_engine: "desktop",
    financial: "financial",
    financial_engine: "financial",
};

function normalizeEngine(engine: string): string {
    return engine.trim().toLowerCase();
}

export default function EvidenceSourcesPage() {

    const params = useParams();

    const workspaceId = Number(params.workspaceId);

    const [
        sources,
        setSources,
    ] = useState<EvidenceAcquisitionSource[]>([]);

    const [
        overview,
        setOverview,
    ] = useState<EvidenceAcquisitionOverview | null>(null);

    useEffect(() => {

        async function load() {

            try {

                const [
                    sourceResponse,
                    overviewResponse,
                ] = await Promise.all([
                    getEvidenceAcquisitionSources(
                        workspaceId,
                    ),
                    getEvidenceAcquisitionOverview(
                        workspaceId,
                    ),
                ]);

                setSources(
                    sourceResponse,
                );

                setOverview(
                    overviewResponse,
                );

            } catch (error) {

                console.error(
                    "Failed to load Evidence Acquisition Sources",
                    error,
                );

            }

        }

        if (
            !Number.isNaN(
                workspaceId,
            )
        ) {

            load();

        }

    }, [
        workspaceId,
    ]);

    return (

        <div className="min-h-screen bg-slate-50">

            <Navbar />

            <div className="mx-auto max-w-7xl px-6 py-10">

                {/* ====================================================== */}
                {/* Hero */}
                {/* ====================================================== */}

                <div className="mb-10">

                    <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
                        INSTITUTIONAL PROVIDER REGISTRY
                    </div>

                    <h1 className="mt-2 text-5xl font-bold">
                        Sources
                    </h1>

                    <p className="mt-4 max-w-5xl leading-7 text-slate-600">
                        Institutional registry of every evidence provider
                        connected to the Evidence Acquisition Runtime. Sources
                        include broker gateways, desktop trading platforms,
                        financial institutions and future acquisition providers.
                    </p>

                </div>

                {/* ====================================================== */}
                {/* Executive Summary */}
                {/* ====================================================== */}

                <div className="mb-8 grid gap-4 lg:grid-cols-6">

                    <MetricCard
                        title="Providers"
                        value={
                            overview?.providers.total ?? 0
                        }
                    />

                    <MetricCard
                        title="Verified"
                        value={
                            sources.filter(
                                (provider) => provider.certified
                            ).length
                        }
                    />

                    <MetricCard
                        title="Active"
                        value={
                            overview?.providers.active ?? 0
                        }
                    />

                    <MetricCard
                        title="Synchronizing"
                        value={
                            overview?.providers.synchronizing ?? 0
                        }
                    />

                    <MetricCard
                        title="Failed"
                        value={
                            overview?.providers.failed ?? 0
                        }
                    />

                    <MetricCard
                        title="Engines"
                        value={
                            overview?.runtime.registered_engines ?? 0
                        }
                    />

                </div>

                {/* ====================================================== */}
                {/* Gateway Providers */}
                {/* ====================================================== */}

                <ProviderSection
                    title="Gateway Providers"
                    description="REST APIs, FIX, WebSocket, Exchange APIs and broker gateway providers."
                >

                    <ProviderTable

                        workspaceId={workspaceId}

                        rows={

                            sources.filter(
                                (provider) =>
                                    normalizeEngine(provider.engine) === "gateway_trading_engine" ||
                                    normalizeEngine(provider.engine) === "gateway",
                            ).map(

                                (provider) => ({

                                    id: provider.name.toLowerCase(),

                                    provider: provider.name,

                                    engine: provider.engine,

                                    status: provider.connected
                                        ? "Connected"
                                        : "Not Connected",

                                    health: provider.active
                                        ? "Healthy"
                                        : "Offline",

                                }),

                            )

                        }
                    />

                </ProviderSection>

                {/* ====================================================== */}
                {/* Desktop Providers */}
                {/* ====================================================== */}

                <ProviderSection
                    title="Desktop Trading Providers"
                    description="Institutional desktop trading platforms."
                >

                    <ProviderTable

                        workspaceId={workspaceId}

                        rows={

                            sources.filter(
                                (provider) =>
                                    normalizeEngine(provider.engine) === "desktop_trading_engine" ||
                                    normalizeEngine(provider.engine) === "desktop",
                            ).map(

                                (provider) => ({

                                    id: provider.name.toLowerCase(),

                                    provider: provider.name,

                                    engine: provider.engine,

                                    status: provider.connected
                                        ? "Connected"
                                        : "Not Connected",

                                    health: provider.active
                                        ? "Healthy"
                                        : "Offline",

                                }),

                            )

                        }
                    />

                </ProviderSection>

                {/* ====================================================== */}
                {/* Financial Providers */}
                {/* ====================================================== */}

                <ProviderSection
                    title="Financial Providers"
                    description="Financial networks and institutional infrastructure."
                >

                    <ProviderTable

                        workspaceId={workspaceId}
                        
                        rows={

                            sources.filter(
                                (provider) =>
                                    normalizeEngine(provider.engine) === "financial_engine" ||
                                    normalizeEngine(provider.engine) === "financial",
                            ).map(

                                (provider) => ({

                                    id: provider.name.toLowerCase(),

                                    provider: provider.name,

                                    engine: provider.engine,

                                    status: provider.connected
                                        ? "Connected"
                                        : "Not Connected",

                                    health: provider.active
                                        ? "Healthy"
                                        : "Offline",

                                }),

                            )

                        }
                    />

                </ProviderSection>

                {/* ====================================================== */}
                {/* Provider Health */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">
                        Provider Health
                    </h2>

                    <p className="mt-2 text-slate-500">
                        Operational status of provider infrastructure.
                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-4">

                        <HealthCard
                            title="Gateway Engine"
                            status={
                                !overview
                                    ? "LOADING"
                                    : !overview.engines.gateway.registered
                                        ? "NOT REGISTERED"
                                        : overview.engines.gateway.healthy
                                            ? "HEALTHY"
                                            : "UNHEALTHY"
                            }
                        />

                        <HealthCard
                            title="Desktop Engine"
                            status={
                                !overview
                                    ? "LOADING"
                                    : !overview.engines.desktop.registered
                                        ? "NOT REGISTERED"
                                        : overview.engines.desktop.healthy
                                            ? "HEALTHY"
                                            : "UNHEALTHY"
                            }
                        />

                        <HealthCard
                            title="Financial Engine"
                            status={
                                !overview
                                    ? "LOADING"
                                    : !overview.engines.financial.registered
                                        ? "NOT REGISTERED"
                                        : overview.engines.financial.healthy
                                            ? "HEALTHY"
                                            : "UNHEALTHY"
                            }
                        />

                        <HealthCard
                            title="Provider Registry"
                            status={
                                !overview
                                    ? "LOADING"
                                    : overview.providers.total > 0
                                        ? "ACTIVE"
                                        : "EMPTY"
                            }
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Activity */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8">

                    <h2 className="text-3xl font-semibold">
                        Recent Provider Activity
                    </h2>

                    <p className="mt-2 text-slate-500">
                        Provider events and synchronization history will appear
                        here once runtime integration is enabled.
                    </p>

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

function ProviderSection({
    title,
    description,
    children,
}: {
    title: string;
    description: string;
    children: React.ReactNode;
}) {

    return (

        <div className="rounded-2xl border bg-white p-8 mb-8">

            <h2 className="text-3xl font-semibold">
                {title}
            </h2>

            <p className="mt-2 text-slate-500">
                {description}
            </p>

            <div className="mt-8">
                {children}
            </div>

        </div>

    );

}

function ProviderTable({

    workspaceId,

    rows,

}:{

    workspaceId:number;

    rows: {

        id: string;

        provider: string;

        engine: string;

        status: string;

        health: string;

    }[];
}) {

    return (

        <table className="w-full">

            <thead>

                <tr className="border-b text-left">

                    <th className="pb-4">Provider</th>
                    <th className="pb-4">Engine</th>
                    <th className="pb-4">Connection</th>
                    <th className="pb-4">Health</th>

                </tr>

            </thead>

            <tbody>

                {rows.map((row) => (

                    <tr
                        key={row.provider}
                        className="border-b"
                    >

                        <td className="py-4 font-medium">

                            <Link

                                href={`/workspace/${workspaceId}/sources/${
                                    ENGINE_ROUTE_MAP[normalizeEngine(row.engine)] ?? "unknown"
                                }/${row.id}`}

                                className="text-blue-600 hover:underline"

                            >

                                {row.provider}

                            </Link>

                        </td>

                        <td>
                            {ENGINE_ROUTE_MAP[normalizeEngine(row.engine)] ?? row.engine}
                        </td>

                        <td>{row.status}</td>

                        <td>{row.health}</td>

                    </tr>

                ))}

            </tbody>

        </table>

    );

}

function HealthCard({
    title,
    status,
}: {
    title: string;
    status: string;
}) {

    return (

        <div className="rounded-xl border bg-slate-50 p-6">

            <div className="font-semibold">
                {title}
            </div>

            <div className="mt-6 inline-flex rounded-full bg-green-100 px-3 py-1 text-sm font-semibold text-green-700">
                {status}
            </div>

        </div>

    );

}