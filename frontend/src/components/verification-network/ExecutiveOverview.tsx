"use client";

import { VerificationAnalytics } from "@/lib/api";

interface Props {
    data: VerificationAnalytics;
}

export default function ExecutiveOverview({
    data,
}: Props) {

    const trust =
        data.executive.workspace_trust_score;

    const health =
        data.executive.network_health;

    const band =
        data.executive.verification_band;

    const allocator =
        data.executive.allocator_ready;

    return (

        <div className="rounded-2xl border bg-white p-8 shadow-sm">

            <div className="flex items-start justify-between">

                <div>

                    <div className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">

                        Institutional Verification Intelligence

                    </div>

                    <h1 className="mt-3 text-4xl font-bold">

                        Verification Network

                    </h1>

                    <p className="mt-3 max-w-3xl text-slate-600">

                        Executive trust intelligence showing the overall
                        verification posture, publication readiness,
                        governance health and institutional confidence of
                        this workspace.

                    </p>

                </div>

                <div
                    className={`
                        rounded-xl
                        px-4
                        py-3
                        text-sm
                        font-semibold
                        ${
                            allocator
                                ? "bg-green-50 text-green-700 border border-green-200"
                                : "bg-amber-50 text-amber-700 border border-amber-200"
                        }
                    `}
                >
                    {allocator
                        ? "ALLOCATOR READY"
                        : "UNDER REVIEW"}
                </div>

            </div>

            <div className="mt-8 grid gap-5 md:grid-cols-4">

                <Metric
                    title="Workspace Trust"
                    value={`${trust}%`}
                    subtitle="Institutional Trust Score"
                />

                <Metric
                    title="Network Health"
                    value={health}
                    subtitle="Operational Status"
                />

                <Metric
                    title="Verification Band"
                    value={band}
                    subtitle="Institutional Rating"
                />

                <Metric
                    title="Coverage"
                    value={`${data.coverage.verification}%`}
                    subtitle="Verification Coverage"
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

            <div className="mt-3 text-3xl font-bold">

                {value}

            </div>

            <div className="mt-2 text-sm text-slate-500">

                {subtitle}

            </div>

        </div>

    );

}