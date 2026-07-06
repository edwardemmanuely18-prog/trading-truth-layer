"use client";

import { VerificationAnalytics } from "@/lib/api";

interface Props {

    data: VerificationAnalytics;

}

export default function BrokerNetwork({

    data,

}: Props) {

    const broker = data.broker_network;

    const health =

        broker.total_accounts === 0

            ? "No Brokers"

            : broker.verified === broker.total_accounts

            ? "Fully Verified"

            : broker.verified >= broker.total_accounts / 2

            ? "Partially Verified"

            : "Verification Required";

    return (

        <div className="rounded-2xl border bg-white p-8 shadow-sm">

            <div className="flex items-center justify-between">

                <div>

                    <div className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">

                        Institutional Infrastructure

                    </div>

                    <h2 className="mt-2 text-2xl font-bold">

                        Broker Verification Network

                    </h2>

                    <p className="mt-2 max-w-3xl text-slate-600">

                        Monitor broker connectivity, verification status,
                        live account coverage and provider diversity across
                        the workspace.

                    </p>

                </div>

                <div
                    className={`rounded-xl px-4 py-2 text-sm font-semibold ${
                        health === "Fully Verified"
                            ? "border border-green-200 bg-green-50 text-green-700"
                            : health === "Partially Verified"
                            ? "border border-amber-200 bg-amber-50 text-amber-700"
                            : "border border-slate-200 bg-slate-50 text-slate-700"
                    }`}
                >
                    {health}
                </div>

            </div>

            <div className="mt-8 grid gap-5 md:grid-cols-4">

                <Metric
                    title="Broker Accounts"
                    value={broker.total_accounts}
                />

                <Metric
                    title="Verified"
                    value={broker.verified}
                />

                <Metric
                    title="Live Accounts"
                    value={broker.live}
                />

                <Metric
                    title="Providers"
                    value={broker.providers.length}
                />

            </div>

            <div className="mt-8 rounded-xl border bg-slate-50 p-5">

                <div className="mb-4 text-sm font-semibold">

                    Connected Providers

                </div>

                {broker.providers.length === 0 ? (

                    <div className="text-sm text-slate-500">

                        No connected broker providers.

                    </div>

                ) : (

                    <div className="flex flex-wrap gap-2">

                        {broker.providers.map((provider) => (

                            <span
                                key={provider}
                                className="rounded-full border bg-white px-3 py-1 text-sm"
                            >
                                {provider}
                            </span>

                        ))}

                    </div>

                )}

            </div>

        </div>

    );

}

interface MetricProps {

    title: string;

    value: string | number;

}

function Metric({

    title,

    value,

}: MetricProps) {

    return (

        <div className="rounded-xl border bg-slate-50 p-5">

            <div className="text-xs uppercase tracking-wider text-slate-500">

                {title}

            </div>

            <div className="mt-3 text-4xl font-bold">

                {value}

            </div>

        </div>

    );

}