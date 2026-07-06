"use client";

import { VerificationAnalytics } from "@/lib/api";

interface Props {

    data: VerificationAnalytics;

}

export default function TrustCoverage({

    data,

}: Props) {

    return (

        <div className="rounded-2xl border bg-white p-8 shadow-sm">

            <div className="flex items-center justify-between">

                <div>

                    <div className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">

                        Verification Coverage

                    </div>

                    <h2 className="mt-2 text-2xl font-bold">

                        Institutional Coverage Metrics

                    </h2>

                    <p className="mt-2 max-w-3xl text-slate-600">

                        Coverage measures indicate how much of the
                        workspace has progressed through institutional
                        verification, publication and governance.

                    </p>

                </div>

            </div>

            <div className="mt-8 space-y-7">

                <CoverageBar

                    title="Verification Coverage"

                    value={data.coverage.verification}

                    color="bg-blue-600"

                />

                <CoverageBar

                    title="Publication Coverage"

                    value={data.coverage.publication}

                    color="bg-emerald-600"

                />

                <CoverageBar

                    title="Lock Coverage"

                    value={data.coverage.lock}

                    color="bg-violet-600"

                />

            </div>

        </div>

    );

}

interface CoverageBarProps {

    title: string;

    value: number;

    color: string;

}

function CoverageBar({

    title,

    value,

    color,

}: CoverageBarProps) {

    return (

        <div>

            <div className="mb-2 flex justify-between">

                <span className="font-medium">

                    {title}

                </span>

                <span className="font-semibold">

                    {value.toFixed(1)}%

                </span>

            </div>

            <div className="h-3 rounded-full bg-slate-200">

                <div

                    className={`${color} h-3 rounded-full transition-all duration-700`}

                    style={{

                        width: `${Math.min(value,100)}%`,

                    }}

                />

            </div>

        </div>

    );

}