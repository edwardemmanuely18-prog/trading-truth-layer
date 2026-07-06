"use client";

import { VerificationAnalytics } from "@/lib/api";

interface Props {

    data: VerificationAnalytics;

}

export default function LifecyclePipeline({

    data,

}: Props) {

    const total =

        Math.max(

            1,

            data.lifecycle.draft +

            data.lifecycle.verified +

            data.lifecycle.published +

            data.lifecycle.locked,

        );

    return (

        <div className="rounded-2xl border bg-white p-8 shadow-sm">

            <div className="mb-8">

                <div className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">

                    Institutional Lifecycle

                </div>

                <h2 className="mt-2 text-2xl font-bold">

                    Claim Verification Pipeline

                </h2>

                <p className="mt-2 text-slate-600">

                    Every institutional claim progresses through a governed
                    lifecycle before becoming allocator ready.

                </p>

            </div>

            <div className="grid grid-cols-4 gap-5">

                <Stage

                    title="Draft"

                    count={data.lifecycle.draft}

                    total={total}

                    color="bg-slate-500"

                />

                <Stage

                    title="Verified"

                    count={data.lifecycle.verified}

                    total={total}

                    color="bg-blue-600"

                />

                <Stage

                    title="Published"

                    count={data.lifecycle.published}

                    total={total}

                    color="bg-emerald-600"

                />

                <Stage

                    title="Locked"

                    count={data.lifecycle.locked}

                    total={total}

                    color="bg-violet-600"

                />

            </div>

            <div className="mt-10 flex items-center justify-center gap-6 text-slate-400">

                <Arrow/>

                <Arrow/>

                <Arrow/>

            </div>

            <div className="mt-5 rounded-xl border border-green-200 bg-green-50 p-5">

                <div className="text-sm font-semibold text-green-700">

                    Allocator Ready Condition

                </div>

                <div className="mt-2 text-sm text-green-700">

                    Claims become allocator ready once they are
                    published, locked and available for public
                    verification.

                </div>

            </div>

        </div>

    );

}

interface StageProps {

    title: string;

    count: number;

    total: number;

    color: string;

}

function Stage({

    title,

    count,

    total,

    color,

}: StageProps) {

    const pct =

        (count / total) * 100;

    return (

        <div className="rounded-xl border p-5">

            <div className="text-xs uppercase tracking-wider text-slate-500">

                {title}

            </div>

            <div className="mt-3 text-4xl font-bold">

                {count}

            </div>

            <div className="mt-3 h-2 rounded-full bg-slate-200">

                <div

                    className={`${color} h-2 rounded-full transition-all duration-700`}

                    style={{

                        width: `${pct}%`,

                    }}

                />

            </div>

            <div className="mt-2 text-sm text-slate-500">

                {pct.toFixed(1)}%

            </div>

        </div>

    );

}

function Arrow() {

    return (

        <div className="text-3xl font-light">

            →

        </div>

    );

}