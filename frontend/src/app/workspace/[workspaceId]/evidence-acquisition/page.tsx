"use client";

import {
    useEffect,
    useState,
} from "react";

import {
    useParams,
} from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {

    getEvidenceAcquisitionOverview,

    type EvidenceAcquisitionOverview,

} from "../../../../lib/api";

export default function EvidenceAcquisitionOverviewPage() {

    const params = useParams();

    const workspaceId = Number(
        params.workspaceId,
    );

    const [

        overview,

        setOverview,

    ] = useState<
        EvidenceAcquisitionOverview | null
    >(null);

    const [

        loading,

        setLoading,

    ] = useState(true);

    useEffect(() => {

        async function load() {

            try {

                const response =

                    await getEvidenceAcquisitionOverview(

                        workspaceId,

                    );

                setOverview(

                    response,

                );

            }

            catch (error) {

                console.error(

                    error,

                );

            }

            finally {

                setLoading(

                    false,

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

    if (loading) {

        return (

            <div className="min-h-screen bg-slate-50">

                <Navbar />

                <div className="mx-auto max-w-7xl px-6 py-10">

                    Loading Evidence Acquisition Infrastructure...

                </div>

            </div>

        );

    }

    if (!overview) {

        return (

            <div className="min-h-screen bg-slate-50">

                <Navbar />

                <div className="mx-auto max-w-7xl px-6 py-10">

                    Unable to load Evidence Acquisition.

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
                        INSTITUTIONAL EVIDENCE ACQUISITION INFRASTRUCTURE
                    </div>

                    <h1 className="mt-2 text-5xl font-bold">
                        Evidence Acquisition
                    </h1>

                    <p className="mt-4 max-w-5xl text-slate-600 leading-7">
                        Institutional infrastructure responsible for acquiring,
                        synchronizing, normalizing and preserving canonical
                        evidences from broker gateways, desktop trading
                        platforms, financial networks and future acquisition
                        infrastructures operating across the global capital
                        markets.
                    </p>

                </div>

                {/* ====================================================== */}
                {/* Operational Summary */}
                {/* ====================================================== */}

                <div className="grid gap-4 md:grid-cols-4 mb-8">

                    <MetricCard
                        title="Connected Sources"
                        value={
                            overview.summary.connected_sources
                        }
                    />

                    <MetricCard
                        title="Registered Adapters"
                        value={
                            overview.summary.registered_adapters
                        }
                    />

                    <MetricCard
                        title="Active Synchronizations"
                        value={
                            overview.summary.active_synchronizations
                        }
                    />

                    <MetricCard
                        title="Evidence Packages"
                        value={
                            overview.summary.evidence_packages
                        }
                    />

                </div>

                {/* ====================================================== */}
                {/* Runtime */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">

                        Runtime

                    </h2>

                    <p className="mt-2 text-slate-500">

                        Canonical runtime responsible for
                        orchestrating institutional evidence acquisition.

                    </p>

                    <div className="mt-8 grid gap-4 md:grid-cols-5">

                        <MetricCard

                            title="Runtime State"

                            value={
                                overview.runtime.state
                            }

                        />

                        <MetricCard

                            title="Registered Engines"

                            value={
                                overview.runtime.registered_engines
                            }

                        />

                        <MetricCard

                            title="Running Engines"

                            value={
                                overview.runtime.running_engines
                            }

                        />

                        <MetricCard

                            title="Connections"

                            value={
                                overview.runtime.active_connections
                            }

                        />

                        <MetricCard

                            title="Synchronization Jobs"

                            value={
                                overview.runtime.synchronization_jobs
                            }

                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Core Infrastructure */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">
                        Core Acquisition Infrastructure
                    </h2>

                    <p className="mt-2 text-slate-500">
                        Canonical acquisition infrastructure responsible for
                        collecting evidence from trading, financial and
                        institutional providers.
                    </p>

                    <div className="mt-8 grid gap-4 lg:grid-cols-2">

                        <InfrastructureCard
                            name="Gateway Engine"
                            description={
                                overview.engines.gateway.registered
                                    ? overview.engines.gateway.healthy
                                        ? "Gateway acquisition engine is registered and healthy."
                                        : "Gateway acquisition engine is registered but unhealthy."
                                    : "Gateway acquisition engine is not registered."
                            }
                            status={
                                !overview.engines.gateway.registered
                                    ? "NOT REGISTERED"
                                    : overview.engines.gateway.healthy
                                        ? "READY"
                                        : "UNHEALTHY"
                            }
                        />

                        <InfrastructureCard
                            name="Desktop Trading Engine"
                            description={
                                overview.engines.desktop.registered
                                    ? overview.engines.desktop.healthy
                                        ? "Desktop trading acquisition engine is registered and healthy."
                                        : "Desktop trading acquisition engine is registered but unhealthy."
                                    : "Desktop trading acquisition engine is not registered."
                            }
                            status={
                                !overview.engines.desktop.registered
                                    ? "NOT REGISTERED"
                                    : overview.engines.desktop.healthy
                                        ? "READY"
                                        : "UNHEALTHY"
                            }
                        />

                        <InfrastructureCard
                            name="Financial Engine"
                            description={
                                overview.engines.financial.registered
                                    ? overview.engines.financial.healthy
                                        ? "Financial acquisition engine is registered and healthy."
                                        : "Financial acquisition engine is registered but unhealthy."
                                    : "Financial acquisition engine is not registered."
                            }
                            status={
                                !overview.engines.financial.registered
                                    ? "NOT REGISTERED"
                                    : overview.engines.financial.healthy
                                        ? "READY"
                                        : "UNHEALTHY"
                            }
                        />

                        <InfrastructureCard
                            name="Universal Evidence Adapter"
                            description="Canonical evidence abstraction layer shared across every acquisition engine."
                            status="READY"
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Source Summary */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">
                        Source Summary
                    </h2>

                    <p className="mt-2 text-slate-500">

                        Operational provider registry managed
                        by the Evidence Acquisition Runtime.

                    </p>

                </div>

                <div className="mt-8 grid gap-4 md:grid-cols-5">

                    <MetricCard

                        title="Providers"

                        value={
                            overview.providers.total
                        }

                    />

                    <MetricCard

                        title="Certified"

                        value={
                            overview.providers.certified
                        }

                    />

                    <MetricCard

                        title="Active"

                        value={
                            overview.providers.active
                        }

                    />

                    <MetricCard

                        title="Synchronizing"

                        value={
                            overview.providers.synchronizing
                        }

                    />

                    <MetricCard

                        title="Failed"

                        value={
                            overview.providers.failed
                        }

                    />

                </div>

                {/* ====================================================== */}
                {/* Acquisition Topology */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8 mb-8">

                    <h2 className="text-3xl font-semibold">
                        Acquisition Topology
                    </h2>

                    <p className="mt-2 text-slate-500">
                        Canonical topology of every institutional evidence acquisition
                        engine operating inside Trading Truth Layer.
                    </p>

                    <div className="mt-8 overflow-x-auto">

                        <table className="min-w-full border-collapse">

                            <thead>

                                <tr className="border-b">

                                    <th className="py-3 text-left">
                                        Engine
                                    </th>

                                    <th className="py-3 text-left">
                                        Registered
                                    </th>

                                    <th className="py-3 text-left">
                                        Healthy
                                    </th>

                                    <th className="py-3 text-left">
                                        Responsibility
                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                <TopologyRow
                                    name="Gateway Engine"
                                    registered={overview.engines.gateway.registered}
                                    healthy={overview.engines.gateway.healthy}
                                    responsibility="Broker APIs, REST, FIX, WebSocket, gRPC"
                                />

                                <TopologyRow
                                    name="Desktop Trading Engine"
                                    registered={overview.engines.desktop.registered}
                                    healthy={overview.engines.desktop.healthy}
                                    responsibility="MT4, MT5, IBKR, cTrader, NinjaTrader"
                                />

                                <TopologyRow
                                    name="Financial Engine"
                                    registered={overview.engines.financial.registered}
                                    healthy={overview.engines.financial.healthy}
                                    responsibility="SWIFT, Banks, Custodians, Treasury"
                                />

                            </tbody>

                        </table>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Readiness */}
                {/* ====================================================== */}

                <div className="rounded-2xl border bg-white p-8">

                    <h2 className="text-3xl font-semibold">
                        Infrastructure Readiness
                    </h2>

                    <p className="mt-2 text-slate-500">
                        Operational readiness of the institutional acquisition
                        platform.
                    </p>

                    <div className="mt-8 grid gap-6 lg:grid-cols-2">

                        <InfrastructureCard
                            name="Acquisition Bridge"
                            description={
                                overview.bridge.healthy
                                    ? "Bridge operational."
                                    : "Bridge requires attention."
                            }
                            status={
                                overview.bridge.healthy
                                    ? "HEALTHY"
                                    : "OFFLINE"
                            }
                        />

                        <InfrastructureCard
                            name="Runtime"
                            description={
                                overview.runtime.state
                            }
                            status={
                                overview.runtime.state.toUpperCase()
                            }
                        />

                        <InfrastructureCard
                            name="Provider Registry"
                            description={
                                overview.providers.total > 0
                                    ? `${overview.providers.total} providers registered`
                                    : "No providers registered."
                            }
                            status={
                                overview.providers.active > 0
                                    ? "ACTIVE"
                                    : overview.providers.total > 0
                                        ? "REGISTERED"
                                        : "EMPTY"
                            }
                        />

                        <InfrastructureCard
                            name="Universal Evidence Adapter"
                            description="Canonical evidence normalization layer."
                            status="READY"
                        />

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

function InfrastructureCard({
    name,
    description,
    status,
}: {
    name: string;
    description: string;
    status: string;
}) {

    return (

        <div className="rounded-2xl border bg-slate-50 p-6">

            <div className="text-lg font-semibold">
                {name}
            </div>

            <div className="mt-3 text-sm leading-6 text-slate-600">
                {description}
            </div>

            <div
                className={`mt-6 inline-flex rounded-full px-3 py-1 text-sm font-semibold ${
                    status === "READY" ||
                    status === "HEALTHY" ||
                    status === "RUNNING" ||
                    status === "ACTIVE"
                        ? "bg-green-100 text-green-700"
                        : status === "REGISTERED"
                            ? "bg-blue-100 text-blue-700"
                            : status === "NOT REGISTERED" ||
                            status === "OFFLINE" ||
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

function TopologyRow({

    name,

    registered,

    healthy,

    responsibility,

}:{

    name:string;

    registered:boolean;

    healthy:boolean;

    responsibility:string;

}){

    return(

        <tr className="border-b">

            <td className="py-4 font-medium">

                {name}

            </td>

            <td>

                {registered ? "YES" : "NO"}

            </td>

            <td>

                {healthy ? "HEALTHY" : "OFFLINE"}

            </td>

            <td className="text-slate-600">

                {responsibility}

            </td>

        </tr>

    );

}