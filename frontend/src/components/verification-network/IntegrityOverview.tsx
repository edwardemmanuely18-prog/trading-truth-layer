"use client";

import { VerificationAnalytics } from "@/lib/api";

interface Props {

    data: VerificationAnalytics;

}

export default function IntegrityOverview({

    data,

}: Props) {

    const integrity = data.integrity;

    const score = Math.max(

        0,

        100 - integrity.total_alerts * 5,

    );

    const status =

        score >= 90

            ? {

                  label: "Excellent",

                  color:
                      "bg-green-50 border-green-200 text-green-700",

              }

            : score >= 75

            ? {

                  label: "Healthy",

                  color:
                      "bg-blue-50 border-blue-200 text-blue-700",

              }

            : score >= 50

            ? {

                  label: "Warning",

                  color:
                      "bg-amber-50 border-amber-200 text-amber-700",

              }

            : {

                  label: "Critical",

                  color:
                      "bg-red-50 border-red-200 text-red-700",

              };

    return (

        <div className="rounded-2xl border bg-white p-8 shadow-sm">

            <div className="flex items-center justify-between">

                <div>

                    <div className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">

                        Governance & Compliance

                    </div>

                    <h2 className="mt-2 text-2xl font-bold">

                        Integrity Monitoring

                    </h2>

                    <p className="mt-2 max-w-3xl text-slate-600">

                        Continuous monitoring of integrity findings,
                        governance violations and operational health
                        across the verification network.

                    </p>

                </div>

                <div

                    className={`rounded-xl border px-4 py-3 font-semibold ${status.color}`}

                >

                    {status.label}

                </div>

            </div>

            <div className="mt-8 grid gap-5 md:grid-cols-4">

                <Metric

                    title="Integrity Score"

                    value={`${score}%`}

                    subtitle="Overall Health"

                />

                <Metric

                    title="Total Alerts"

                    value={integrity.total_alerts}

                    subtitle="Detected"

                />

                <Metric

                    title="Critical Alerts"

                    value={integrity.critical}

                    subtitle="Requires Action"

                />

                <Metric

                    title="Resolved"

                    value={integrity.resolved}

                    subtitle="Successfully Closed"

                />

            </div>

            <div className="mt-8 rounded-xl border bg-slate-50 p-6">

                <div className="mb-4 text-sm font-semibold">

                    Integrity Assessment

                </div>

                <div className="h-4 rounded-full bg-slate-200">

                    <div

                        className="h-4 rounded-full bg-green-600 transition-all duration-700"

                        style={{

                            width: `${score}%`,

                        }}

                    />

                </div>

                <div className="mt-3 text-sm text-slate-600">

                    The integrity score reflects unresolved alerts,
                    governance findings and operational health of the
                    workspace.

                </div>

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