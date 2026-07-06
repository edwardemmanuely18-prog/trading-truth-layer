"use client";

import { VerificationAnalytics } from "@/lib/api";

interface Props {

    data: VerificationAnalytics;

}

export default function PublicNetwork({

    data,

}: Props) {

    const publicClaims =
        data.visibility.public ?? 0;

    const privateClaims =
        data.visibility.private ?? 0;

    const unlisted =
        data.visibility.unlisted ?? 0;

    const total =
        Math.max(
            1,
            publicClaims +
            privateClaims +
            unlisted,
        );

    const publicPct =
        (publicClaims / total) * 100;

    return (

        <div className="rounded-2xl border bg-white p-8 shadow-sm">

            <div className="flex items-center justify-between">

                <div>

                    <div className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">

                        Public Trust Layer

                    </div>

                    <h2 className="mt-2 text-2xl font-bold">

                        Verification Network Exposure

                    </h2>

                    <p className="mt-2 max-w-3xl text-slate-600">

                        Shows how much of this workspace is discoverable,
                        publicly verifiable and allocator accessible.

                    </p>

                </div>

                <div className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-700">

                    {publicPct.toFixed(1)}%

                    Public Exposure

                </div>

            </div>

            <div className="mt-8 grid gap-5 md:grid-cols-3">

                <Metric

                    title="Public Claims"

                    value={publicClaims}

                    subtitle="Visible"

                />

                <Metric

                    title="Private Claims"

                    value={privateClaims}

                    subtitle="Internal"

                />

                <Metric

                    title="Unlisted"

                    value={unlisted}

                    subtitle="Restricted"

                />

            </div>

            <div className="mt-8">

                <div className="mb-2 flex justify-between">

                    <span className="font-medium">

                        Public Visibility

                    </span>

                    <span className="font-semibold">

                        {publicPct.toFixed(1)}%

                    </span>

                </div>

                <div className="h-4 rounded-full bg-slate-200">

                    <div

                        className="h-4 rounded-full bg-blue-600 transition-all duration-700"

                        style={{

                            width: `${publicPct}%`,

                        }}

                    />

                </div>

            </div>

            <div className="mt-8 grid gap-4 md:grid-cols-4">

                <StatusCard

                    title="Verification Routes"

                    active={publicClaims > 0}

                />

                <StatusCard

                    title="Public Claim Pages"

                    active={publicClaims > 0}

                />

                <StatusCard

                    title="Allocator Discovery"

                    active={publicClaims > 0}

                />

                <StatusCard

                    title="Institutional Visibility"

                    active={publicPct >= 50}

                />

            </div>

        </div>

    );

}

interface MetricProps {

    title: string;

    value: string | number;

    subtitle: string;

}

function Metric({

    title,

    value,

    subtitle,

}: MetricProps) {

    return (

        <div className="rounded-xl border bg-slate-50 p-5">

            <div className="text-xs uppercase tracking-wider text-slate-500">

                {title}

            </div>

            <div className="mt-3 text-4xl font-bold">

                {value}

            </div>

            <div className="mt-2 text-sm text-slate-500">

                {subtitle}

            </div>

        </div>

    );

}

interface StatusCardProps {

    title: string;

    active: boolean;

}

function StatusCard({

    title,

    active,

}: StatusCardProps) {

    return (

        <div

            className={`rounded-xl border p-5 ${

                active

                    ? "border-green-200 bg-green-50"

                    : "border-slate-200 bg-slate-50"

            }`}

        >

            <div className="text-sm font-semibold">

                {title}

            </div>

            <div

                className={`mt-4 inline-flex rounded-full px-3 py-1 text-xs font-semibold ${

                    active

                        ? "bg-green-600 text-white"

                        : "bg-slate-300 text-slate-700"

                }`}

            >

                {active ? "ACTIVE" : "INACTIVE"}

            </div>

        </div>

    );

}